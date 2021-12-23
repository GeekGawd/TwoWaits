from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.fields.related import OneToOneField

from Accounts.models import UserAccount


class Faculty(models.Model):
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('O', 'Others'))
    QUALIFICATION = (('P', 'Postgraduate'), ('U', 'Undergraduate'))

    faculty_account_id = models.OneToOneField(UserAccount, on_delete=models.CASCADE, related_name='faculty')
    name = models.CharField(max_length=30, )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    mobile = models.BigIntegerField(blank=True, null=True, validators=[MinValueValidator(1000000000), MaxValueValidator(9999999999)])
    college = models.CharField(max_length=40, blank=True, null=True)
    experience = models.CharField(max_length=50, blank=True, null=True)
    qualification = models.CharField(max_length=10, choices=QUALIFICATION)
    profile_pic = models.ImageField(upload_to = 'ProfilePic' ,default = 'ProfilePic/Avatar1.png')
    
    def __str__(self):
        return self.name
        