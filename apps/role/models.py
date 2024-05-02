from django.db import models

class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=100)
    # permissions field will be added later (acting as a foreign key to the Permission model)

    def __str__(self):
        return self.role_name
