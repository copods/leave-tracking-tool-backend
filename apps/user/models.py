import datetime
from django.db import models
import uuid
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .constants import *
from ..role.models import Role
from ..department.models import Department

def validate_phone_number(value):
    if len(str(value)) != 10:
        raise ValidationError(
            _('%(value)s is not a valid phone number.'),
            params={'value': value},
        )

# USER-CLASS
class User(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    doj = models.DateField()
    phone_number = models.BigIntegerField(validators=[validate_phone_number])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    work_status = models.CharField(max_length=3, choices=WORK_STATUS_CHOICES)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    dob = models.DateField(default=datetime.date.today)
    designation = models.CharField(max_length=100, null=True)
    work_location = models.CharField(max_length=100, null=True)
    current_address_line = models.CharField(max_length=200, null=False, default='')
    current_address_city = models.CharField(max_length=100, null=False, default='')
    current_address_state = models.CharField(max_length=100, null=False, default='')
    current_address_pincode = models.IntegerField(default=0, null=False)
    permanent_address_line = models.CharField(max_length=200, null=False, default='')
    permanent_address_city = models.CharField(max_length=100, null=False, default='')
    permanent_address_state = models.CharField(max_length=100, null=False, default='') 
    permanent_address_pincode = models.IntegerField(default=0, null=False)  
    emergency_contact_name = models.CharField(max_length=100, null=True)
    emergency_contact_number = models.BigIntegerField(validators=[validate_phone_number],  null=True)
    emergency_contact_relation = models.CharField(max_length=100, null=True)
    emergency_contact_email = models.EmailField(max_length=100, null=True)
    
    def short_name(self):
        return self.first_name
    
    def long_name(self):
        return f'{self.first_name} {self.last_name}'
