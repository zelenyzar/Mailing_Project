from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя с email как логином."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Пользователи должны иметь email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)



class User(AbstractUser):
    """
    Кастомная модель пользователя.
    Используем email как логин.
    """
    email = models.EmailField(unique=True, verbose_name='Email')

    # Поле для токена подтверждения регистрации
    verification_token = models.CharField(max_length=32, null=True, blank=True)

    # Дата истечения токена
    token_expires_at = models.DateTimeField(null=True, blank=True)

    username = None

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

