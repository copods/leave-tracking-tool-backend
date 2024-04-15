from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [
    path("admin/", admin.site.urls),
    
    #GOOGLE SERVICE
    path(
        "google_sso/", include("django_google_sso.urls", namespace="django_google_sso")
    ),
    #APP
    path('api/', include('apps.api.v1.urls')),
    
    #DEBUGGER
    path("__debug__/", include("debug_toolbar.urls")),
    
    
    # path('home/', TemplateView.as_view(template_name='home.html'), name='home'),
    # path('accounts/', include('allauth.urls')),
    # path('accounts/', include('allauth.socialaccount.urls')),
    # path('o/', include('oauth2_provider.urls', namespace='oauth2_provider'))
]
