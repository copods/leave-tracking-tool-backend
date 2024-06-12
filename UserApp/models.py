from django.db import models
import uuid
from django.forms import ValidationError
from django.utils.timezone import now


# Create your models here.
def validate_phone_number(value):
    if len(str(value)) != 10:
        raise ValidationError(
            ('%(value)s is not a valid phone number.'),
            params={'value': value},
        )

class Department(models.Model):
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True, verbose_name="Public identifier")
    department_key = models.CharField(max_length=100)
    department_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.department_name

class Role(models.Model):
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True, verbose_name="Public identifier")
    role_key = models.CharField(max_length=100)
    role_name = models.CharField(max_length=100)
    permissions = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.role_name

class User(models.Model):
    # Basic Information
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True, verbose_name="Public identifier")
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES
    )
    date_of_birth = models.DateField()
    profile_image = models.CharField(max_length=250)


    # Work Information
    date_of_joining = models.DateField()
    EMPLOYMENT_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract')
    ] # Employement type information (is necessary to keep in db)
    WORK_TYPE_CHOICES = [
        ('In-Office', 'In-Office'),
        ('Work-From-Home', 'Work-From-Home')
    ]
    work_type = models.CharField(   
        max_length=15,
        choices=WORK_TYPE_CHOICES,
        null=True
    )
    designation = models.CharField(max_length=100, null=True)
    work_location = models.CharField(max_length=100, null=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    department= models.ForeignKey(Department, on_delete=models.PROTECT, null=True)

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
    
    #Metadata
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email
    def short_name(self):
        return self.first_name
    def long_name(self):
        return f'{self.first_name} {self.last_name}'