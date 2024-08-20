from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # users crud operations
    path("api/v1/", include("UserApp.urls")),

    # leave crud operations
    path("api/v1/", include("LeaveTrackingApp.urls")),

    # notification related operations
    path("api/v1/", include("PushNotificationApp.urls")),
    
    #DEBUGGER
    path("__debug__/", include("debug_toolbar.urls")),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)