from django.db import models
from UserApp.models import User
import uuid
from django.utils.timezone import now  # Import the now function

# Create your models here.

class RuleSet(models.Model):
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True, verbose_name="Public identifier")
    name = models.CharField(max_length=100)
    max_days_allowed = models.IntegerField()
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
    type = models.CharField(max_length=100)
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
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    approver = models.ForeignKey(User, on_delete=models.CASCADE)
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
    status_reasons = models.ManyToManyField(StatusReason)
    start_date = models.DateField()
    end_date = models.DateField()
    day_details = models.ManyToManyField(DayDetails)
    assets_documents = models.FileField()
    createdAt = models.DateTimeField(default=now)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.leave_type