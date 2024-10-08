from django.db import models
import uuid
from django.utils.timezone import now
from UserApp.managers import UserManager
from UserApp.signals import user_pre_soft_delete_signal


# Create your models here.
def validate_phone_number(value):
    # custom validation later
    return

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
    phone_number = models.CharField(max_length=20)
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )
    date_of_birth = models.DateField()
    profile_image = models.CharField(max_length=250, null=True, blank=True)

    # Work Information
    date_of_joining = models.DateField()
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract')
    ] # Employement type information (is necessary to keep in db)
    WORK_TYPE_CHOICES = [
        ('in_office', 'In-Office'),
        ('work_from_home', 'Work-From-Home')
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
    is_current_address_same = models.BooleanField(default=True)

    # Emergency Contact Information
    emergency_contact_name = models.CharField(max_length=100, null=True)
    emergency_contact_number = models.CharField(max_length=20, null=True)
    emergency_contact_relation = models.CharField(max_length=100, null=True)
    emergency_contact_email = models.EmailField(max_length=100, null=True)

    #user points
    points = models.IntegerField(default=0)
    
    #Metadata
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    app_registration_status = models.BooleanField(default=False)
    onboarding_status = models.JSONField(null=True)

    objects = UserManager()

    def delete(self):
        try:
            user_pre_soft_delete_signal.send(sender=self.__class__, instance=self)
            self.is_deleted = True
            self.save()
        except ValueError as e:
            raise e
        
    @property
    def work_type_choices(self):
        return dict(self.WORK_TYPE_CHOICES).get(self.work_type)
    
    @property
    def employment_type_choices(self):
        return dict(self.EMPLOYMENT_TYPE_CHOICES).get(self.employment_type)
        
    def __str__(self):
        return self.email
    def short_name(self):
        return self.first_name
    def long_name(self):
        return f'{self.first_name} {self.last_name}'