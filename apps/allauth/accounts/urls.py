from django.contrib import admin
from django.urls import include, path

from apps.allauth.accounts import views


urlpatterns = [
    path("profile/", views.profile),
]