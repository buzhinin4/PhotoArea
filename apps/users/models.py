from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _

from apps.address.models import Address
from apps.photo.models import Photo
from apps.users.managers import CustomUserManager


class UserType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class User(AbstractUser, PermissionsMixin):
    objects = CustomUserManager()

    phone_number = PhoneNumberField(unique=True, blank=False, null=False)
    email = models.EmailField(db_index=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_type = models.ForeignKey(UserType, on_delete=models.PROTECT, related_name='users_type', null=True, blank=True)

    photo = models.OneToOneField(
        Photo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user',
    )

    date_birth = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Birthday")

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=False,
        blank=True,
        null=True,
        help_text=_('Optional. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }


class Studio(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    address = models.OneToOneField(
        Address,
        on_delete=models.PROTECT,
    )
    base_user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='studio_profile',
    )

    def __str__(self):
        return self.name


class Photographer(models.Model):
    description = models.TextField(blank=True, null=True)
    base_user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='photographer_profile',
    )

    def __str__(self):
        return self.base_user.last_name
