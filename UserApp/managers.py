from django.db import models

class UserManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(isDeleted=False)

    def all_with_deleted(self):
        return super().get_queryset()

