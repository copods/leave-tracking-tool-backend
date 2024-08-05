from PushNotificationApp.models import FCMToken, Notification
from rest_framework import serializers

class FCMTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMToken
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class FetchNotificationsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Notification
        fields = ['id', 'type', 'isRead', 'object_id', 'title', 'subtitle', 'created_at']