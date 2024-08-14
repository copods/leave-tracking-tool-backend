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
    profile_image = serializers.SerializerMethodField('get_profile_image')
    created_by = serializers.CharField(source='created_by.first_name')

    class Meta:
        model = Notification
        fields = ['id', 'type', 'isRead', 'object_id', 'title', 'subtitle', 'created_at', 'profile_image', 'created_by']
    
    def get_profile_image(self, obj):
        return obj.created_by.profile_image