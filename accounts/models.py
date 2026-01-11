from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom user model
    """
    pass


from django.conf import settings
from django.db import models
from money_log.encryption_services import encrypt_field, decrypt_field

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    phone_plain = models.CharField(max_length=15, null=True, blank=True)
    phone_encrypted = models.BinaryField(null=True, blank=True)

    address_plain = models.TextField(null=True, blank=True)
    address_encrypted = models.BinaryField(null=True, blank=True)

    def __str__(self):
        return self.user.username
