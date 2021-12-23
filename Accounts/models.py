from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import EmailValidator

# timezone
from django.utils import timezone
from datetime import timedelta

class CustomAccountManager(BaseUserManager):
    
    def create_superuser(self, email, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_verified', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, password, **other_fields)



    def create_user(self, email, password, **other_fields):
        if not email:
            raise ValueError(_('You must provide an email address'))

        email = self.normalize_email(email)
        # this is done as normalization would result in 
        # 1. abc@GMAIL.COM -> abc@gmail.com
        # 2. ABC@GMAIL.COM -> ABC@gmail.com
        # Since email are unique identifiers in our app 
        # but practically both emails are exactly the same but only normalization would result in redundancy
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save()
        return user

class UserAccount(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_('email address'), validators=[EmailValidator()], unique=True)
    
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

class OTP(models.Model):

    otp_account_id = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='otp')
    otp = models.IntegerField()
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.otp}'
