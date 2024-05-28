from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),

    # users crud operations
    path("api/v1/", include("UserApp.urls")),
    
    #DEBUGGER
    path("__debug__/", include("debug_toolbar.urls")),
    
]
