from django.db import models
import uuid
from django.utils import timezone
from .constants import *

# USER-CLASS
class User(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    doj = models.DateField()
    phone_number = models.CharField(max_length=15)
    emergency_contact = models.CharField(max_length=15)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    work_status = models.CharField(max_length=3, choices=WORK_STATUS_CHOICES)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.email
    def short_name(self):
        return self.first_name
    def long_name(self):
        return f'(self.first_name) (self.last_name)'
    
