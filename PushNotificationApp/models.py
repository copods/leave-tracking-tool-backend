from django.db import models
import uuid
from django.utils.timezone import now
from django.contrib.postgres.fields import ArrayField
from LeaveTrackingApp.models import Leave
from UserApp.models import User  

# Create your models here.
class FCMToken(models.Model):
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True, verbose_name="Public identifier")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    fcm_token = models.CharField(max_length=300,unique=True, verbose_name="FCM tokens")
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.fcm_token
    

class Notification(models.Model):
    id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True, verbose_name="Public identifier")
    TYPES_CHOICES = [
        ('Leave-Request', 'Leave Request'),
        ('Upcoming-Holidays','Upcoming Holidays')
        
    ]
    types = models.CharField(max_length=100,unique=True, verbose_name="notification types", choices=TYPES_CHOICES)
    isRead = models.BooleanField(default=False)
    leaveApplicationId = models.ForeignKey(Leave, on_delete=models.CASCADE, null=True, related_name='leave_request')
    receivers = ArrayField(models.UUIDField())
    title = models.CharField(max_length=100, verbose_name='title')
    subtitle = models.CharField(max_length=300, verbose_name="subtitle")
    redireactionUrl = models.CharField(max_length=250, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_created_by')
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.title} - {self.subtitle}"