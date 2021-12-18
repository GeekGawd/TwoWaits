from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.validators import EmailValidator

class CustomAccountManager(BaseUserManager):

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

class UserAccount(AbstractBaseUser):

    email = models.EmailField(_('email address'), validators=[EmailValidator()], unique=True)
  
    is_verified = models.BooleanField(default=False)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
