from django.db import models
import uuid
from django.utils.timezone import now
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