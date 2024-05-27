from django.db import models
import nanoid

class Department(models.Model):
    dept_id = models.CharField(primary_key=True, max_length=12, default=nanoid.generate(size=11))
    dept_name = models.CharField(max_length=100)

    def __str__(self):
        return self.dept_name
