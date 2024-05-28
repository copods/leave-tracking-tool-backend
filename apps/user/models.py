from django.db import models
import uuid
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from apps.user.constants import GENDER_CHOICES, WORK_STATUS_CHOICES
from apps.role.models import Role

def validate_phone_number(value):
    if len(str(value)) != 10:
        raise ValidationError(
            _('%(value)s is not a valid phone number.'),
            params={'value': value},
        )

# USER-CLASS
class User(models.Model):
    # Basic Information
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Public identifier")
    email = models.EmailField(primary_key=True,unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.BigIntegerField(validators=[validate_phone_number])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    dob = models.DateField()
    profile_image = models.CharField(null=True)
    
    # Work Information
    doj = models.DateField()
    work_type = models.CharField(max_length=3, choices=WORK_STATUS_CHOICES, null=True)
    designation = models.CharField(max_length=100, null=True)
    work_location = models.CharField(max_length=100, null=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT) #foreign key to role model
    
    # Address Information
    current_address_line = models.CharField(max_length=200, null=True)
    current_address_city = models.CharField(max_length=100, null=True)
    current_address_state = models.CharField(max_length=100, null=True)
    current_address_pincode = models.IntegerField(null=True)
    permanent_address_line = models.CharField(max_length=200, null=True)
    permanent_address_city = models.CharField(max_length=100, null=True)
    permanent_address_state = models.CharField(max_length=100, null=True)
    permanent_address_pincode = models.IntegerField(null=True)
    
    # Emergency Contact Information
    emergency_contact_name = models.CharField(max_length=100, null=True)
    emergency_contact_number = models.BigIntegerField(validators=[validate_phone_number],  null=True)
    emergency_contact_relation = models.CharField(max_length=100, null=True)
    emergency_contact_email = models.EmailField(max_length=100, null=True)
    
    # Metadata
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(default=timezone.now)
    
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True) #Foreign key to Role model
     
    def __str__(self):
        return self.email
    def short_name(self):
        return self.first_name
    def long_name(self):
        return f'{self.first_name} {self.last_name}'
