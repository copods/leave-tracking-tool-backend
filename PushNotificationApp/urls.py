from django.urls import path, re_path

from PushNotificationApp.views.push_notification_views import (fcmTokenStore, fcmTokenValidate)

urlpatterns = [
    re_path(r'^fcmTokenStore$', fcmTokenStore),
    re_path(r'^fcmTokenValidate$', fcmTokenValidate),
]
