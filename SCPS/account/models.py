from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_superuser(self, email, user_name, first_name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, user_name, first_name, password, **other_fields)
        # user = self.model(
        #     email=self.normalize_email(email),
        #     username=username,
        # )
        # user.set_password(password)
        # user.save(using=self._db)
        # return user

    def create_user(self, email, user_name, first_name, password, **otherfields):

        if not email:
            raise ValueError("Users must have an email address")
        if not user_name:
            raise ValueError("Users must have an Username")

        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name,
                          first_name=first_name, **otherfields)
        user.set_password(password)
        user.save()
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_MANAGER = 'M'
    ROLE_SYSTEM = 'S'
    ROLE_Customer = 'C'

    ROLE_CHOICES = [
        (ROLE_MANAGER, 'Manager'),
        (ROLE_SYSTEM, 'System'),
        (ROLE_Customer, 'Customer'),
    ]
    # email = models.EmailField(_('email address'), unique=True)
    # user_name = models.CharField(max_length=150, unique=True)

    # start_date = models.DateTimeField(default=timezone.now)
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    user_name = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    password = models.CharField(max_length=30)
    start_date = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default=ROLE_Customer)
    # is_admin = models.BooleanField()
    # is_active = models.BooleanField(default=True)
    # is_staff = models.BooleanField()
    # is_superuser = models.BooleanField()
    about = models.TextField(_(
        'about'), max_length=500, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name', 'first_name']

    def __str__(self):
        return self.user_name

    # def has_perm(self, perm, obj=None):
    #     return self.is_admin
    #
    # def has_module_perms(self, app_label):
    #     return True
# class CustomUser(AbstractBaseUser):
#     ROLE_MANAGER = 'M'
#     ROLE_SYSTEM = 'S'
#     ROLE_Customer = 'C'
#
#     ROLE_CHOICES = [
#         (ROLE_MANAGER, 'Manager'),
#         (ROLE_SYSTEM, 'System'),
#         (ROLE_Customer, 'Customer'),
#     ]
#     email = models.EmailField(verbose_name="email", max_length=60, unique=True)
#     username = models.CharField(max_length=30, unique=True)
#     password = models.CharField(max_length=30)
#     data_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
#     last_login = models.DateTimeField(verbose_name="last login", auto_now=True)
#     role = models.CharField(max_length=1, choices=ROLE_CHOICES, default=ROLE_Customer)
#     is_admin = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)
#
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username', ]
#
#     objects = CustomUserManager()
#
#     def __str__(self):
#         return self.email + " ," + self.username
#
#     def has_perm(self, perm, obj=None):
#         return self.is_admin
#
#     def has_module_perms(self, app_label):
#         return True
