from django.db import models
import uuid
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
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
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True, verbose_name="Public identifier")
    TYPE_CHOICES = [
        ('leave_request', 'Leave Request'),
        ('calendar', 'Calendar'),
        ('leave_policy', 'Leave Policy'),
    ]
    type = models.CharField(max_length=100, verbose_name="notification type", choices=TYPE_CHOICES)
    isRead = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    receivers = ArrayField(models.UUIDField())
    title = models.CharField(max_length=100, verbose_name='title')
    subtitle = models.CharField(max_length=300, verbose_name="subtitle")
    redireactionUrl = models.CharField(max_length=250, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='request_created_by')
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.title} - {self.subtitle}"