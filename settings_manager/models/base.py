import logging
from typing import Any
from django.apps import apps
from django.conf import settings
from django.core.management.color import no_style
from django.db import connection, models
from django.db.utils import IntegrityError
from django.utils.timezone import now

logger = logging.getLogger(__name__)

def get_model(name):
    (app_label, model_name) = name.split(".")
    return apps.get_model(app_label=app_label, model_name=model_name)

class BaseQuerySet(models.QuerySet):
    _active_test_enabled = True

    def set_active_test(self, enabled=True):
        self._active_test_enabled = enabled
        return super().filter()

    def with_active_test(self, enabled=True):
        if enabled:
            self.query.add_q(models.Q(is_active=True))
        return self._chain()

    def _clone(self):
        c = super()._clone()
        c._active_test_enabled = self._active_test_enabled
        return c

    def _fetch_all(self):
        self.with_active_test(self._active_test_enabled)
        return super()._fetch_all()

    def count(self):
        self.with_active_test(self._active_test_enabled)
        return super().count()

    def update(self, *args, **kwargs):
        self.with_active_test(self._active_test_enabled)
        if "is_active" in kwargs:
            if kwargs["is_active"]:
                kwargs["deleted_at"] = None
            else:
                kwargs["deleted_at"] = now()
        return super().update(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.with_active_test(self._active_test_enabled)
        return super().get(*args, **kwargs)

    def delete(self, is_soft=True):
        self.with_active_test(self._active_test_enabled)
        if is_soft:
            return super().update(
                is_active=False,
                deleted_at=now(),
            )
        else:
            return super().delete()

class BaseModelManager(models.Manager):
    def get_queryset(self) -> BaseQuerySet:
        return BaseQuerySet(self.model, using=self._db).set_active_test(enabled=True)

    def _reset_model_sequence(self):
        """Reset the primary key sequence for this model to MAX(id) + 1."""
        sequence_sql = connection.ops.sequence_reset_sql(
            no_style(), [self.model]
        )
        if sequence_sql:
            with connection.cursor() as cursor:
                for statement in sequence_sql:
                    cursor.execute(statement)

    def from_fixture(self, defaults=None, **kwargs) -> tuple[Any, bool]:
        __noupdate__ = kwargs.pop("__noupdate__", False)
        qs = None

        try:
            qs = self.get_queryset().set_active_test(enabled=False)
        except AttributeError as e:
            raise Exception(
                f"'{self.__class__}' does not have an 'active test manager' in its queryset."
            ) from e

        try:
            return self._from_fixture_call(qs, __noupdate__, defaults, **kwargs)
        except IntegrityError as e:
            if "pkey" not in str(e) and "_pkey" not in str(e):
                raise

            # Stale PK sequence — reset for this model and retry once.
            logger.info(
                "PK sequence out of sync for %s, resetting and retrying.",
                self.model.__name__,
            )
            self._reset_model_sequence()
            return self._from_fixture_call(qs, __noupdate__, defaults, **kwargs)

    @staticmethod
    def _from_fixture_call(qs, noupdate, defaults, **kwargs):
        if noupdate:
            if not kwargs:
                return qs.get_or_create(**defaults)
            else:
                return qs.get_or_create(defaults, **kwargs)

        if not kwargs:
            return qs.update_or_create(**defaults)
        else:
            return qs.update_or_create(defaults, **kwargs)

class BaseModel(models.Model):
    objects = BaseModelManager()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
    )

    def delete(self, is_soft=True, *args, **kwargs):
        if is_soft:
            self.is_active = False
            self.deleted_at = now()
            return self.save()
        return super().delete(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = (
            "-updated_at",
            "-created_at",
        )
