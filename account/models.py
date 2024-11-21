from datetime import datetime, timedelta

import jwt
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
import secrets

from afiche import settings


class UserManager(BaseUserManager):
    def _create(self, email, password, **extra_fields):
        if not email:
            raise ValidationError('Email cannot be blank')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.create_activation_code()
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_staff', False)
        return self._create(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        return self._create(email, password, **extra_fields)


class Group(models.Model):
    name = models.CharField(max_length=35)
    course = models.PositiveSmallIntegerField()
    direction = models.CharField(max_length=35, default='КОМТЕХНО')
    stage = models.CharField(max_length=35, blank=True, null=True)


    def __str__(self):
        return f"({self.course}) {self.name}"


class AbstractUser(AbstractBaseUser):
    class UserTypes(models.TextChoices):
        STUDENT = 'student'
        HEADMAN = 'headman'
        TEACHER = 'teacher'

    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=20, unique=True)

    full_name = models.CharField(max_length=60)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)

    user_type = models.CharField(max_length=10, choices=UserTypes.choices)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'phone_number', 'user_type']
    
    activation_code = models.CharField(max_length=8, blank=True)
    objects = UserManager()

    def __str__(self):
        return f'{self.full_name} ({self.group if self.group else f"is_staff={self.is_staff}"}) ({self.user_type})'

    def get_group_name(self):
        return self.group.name

    def create_activation_code(self):
        code = secrets.token_urlsafe(6)
        self.activation_code = code
        self.save()

    def has_module_perms(self, app_label):
        return self.is_staff

    def has_perm(self, perm, obj=None):
        return self.is_staff

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')






