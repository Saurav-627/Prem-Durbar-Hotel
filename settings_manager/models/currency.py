from django.db import models
from .base import BaseModel

class Currency(BaseModel):
    name = models.CharField(max_length=128)
    iso_code = models.CharField(max_length=10, unique=True)
    symbol = models.CharField(max_length=10)
    is_custom = models.BooleanField(default=False)
    sequence = models.SmallIntegerField(blank=False, null=True)
    is_published = models.BooleanField(default=False)

    display_name = models.GeneratedField(
        expression=models.F("name"),
        output_field=models.CharField(max_length=128),
        db_persist=True,
    )

    def __str__(self) -> str:
        return self.display_name
    
    class Meta:
        ordering = ["sequence", "id"]
        indexes = [
            models.Index(fields=["iso_code"]),
        ]

    @classmethod
    def get_by_iso_code(cls, iso_code):
        return cls.objects.filter(iso_code=iso_code).first()
    
    @classmethod
    def get_default_currency(cls):
        return cls.objects.filter(iso_code="USD").first()
    
    @classmethod
    def get_pesa_currency(cls):
        return cls.objects.filter(iso_code="XPESA").first()
    
    @classmethod
    def get_npr_currency(cls):
        return cls.objects.filter(iso_code="NPR").first()
