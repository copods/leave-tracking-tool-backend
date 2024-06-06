from django.db import models
from UserApp.models import User
import uuid
from django.utils.timezone import now  # Import the now function

# Create your models here.

class Holiday(models.Model):
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True, verbose_name="Public identifier")
    date = models.DateField()
    name = models.CharField(max_length=100)
    TYPE_CHOICES = [
        ('Optional', 'Optional'),
        ('Confirmed', 'Confirmed'),
    ]
    type = models.CharField(
        max_length=100,
        choices=TYPE_CHOICES,
        default='Confirmed',
    )
    createdAt = models.DateTimeField(default=now)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class yearCalendar(models.Model):
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True, verbose_name="Public identifier")
    year = models.IntegerField()
    holidays = models.ManyToManyField('Holiday')
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Approved', 'Approved'),
        ('Published', 'Published'),
    ]
    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        default='Draft',
    )
    createdAt = models.DateTimeField(default=now)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.year

class RuleSet(models.Model):
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True, verbose_name="Public identifier")
    name = models.CharField(max_length=100)
    max_days_allowed = models.FloatField()
    duration = models.CharField(default=None, max_length=100)
    createdAt = models.DateTimeField(default=now)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class LeaveType(models.Model):
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True, verbose_name="Public identifier")
    name = models.CharField(max_length=100)
    rule_set = models.ForeignKey(RuleSet, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(default=now)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class StatusReason(models.Model):
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True, verbose_name="Public identifier")
    STATUS_CHOICES = [
        ('P', 'PENDING'),
        ('A', 'APPROVED'),
        ('R', 'REJECTED'),
        ('W', 'WITHDRAWN'),
    ]
    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        default='P',
    )    
    reason = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(default=now)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.status

class DayDetails(models.Model):
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True, verbose_name="Public identifier")
    date = models.DateField()
    type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    is_half_day = models.BooleanField()
    HALF_DAY_CHOICES = [
        ('FH', 'First Half'),
        ('SH', 'Second Half'),
    ]
    half_day_type = models.CharField(
        max_length=2,
        choices=HALF_DAY_CHOICES,
        blank=True, 
        null=True,
    )
    createdAt = models.DateTimeField(default=now)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.date


# Day Details
# date
# type : leave/optional holiday/wfh
# is_half_day
# type (first|second)

class Leave(models.Model):
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True, verbose_name="Public identifier")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_of_leaves')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approver_of_leave')
    leave_reason = models.CharField(max_length=100)
    STATUS_CHOICES = [
        ('P', 'PENDING'),
        ('A', 'APPROVED'),
        ('R', 'REJECTED'),
        ('W', 'WITHDRAWN'),
    ]
    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        default='P',
    )        
    status_reasons = models.ManyToManyField(StatusReason, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    day_details = models.ManyToManyField(DayDetails)
    assets_documents = models.FileField(blank=True, null=True)
    IS_EDITED_CHOICES = [
        ('Edited', 'Edited'),
        ('Requested-For-Edit', 'Requested-For-Edit'),
    ]
    editStatus = models.CharField(max_length=100, null=True, choices=IS_EDITED_CHOICES)
    createdAt = models.DateTimeField(default=now)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.leave_type
