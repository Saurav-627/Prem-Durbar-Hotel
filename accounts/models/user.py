from django.contrib.auth.models import AbstractUser
from django.db import models
from core.utils import UploadTo, ValidateFileSize

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_hotel_admin = models.BooleanField(default=False)
    is_guest = models.BooleanField(default=True)
    avatar = models.ImageField(
        upload_to=UploadTo('avatars'),
        blank=True,
        null=True,
        validators=[ValidateFileSize(2)]
    )

    class Meta:
        db_table = 'auth_user'
