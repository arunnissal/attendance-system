from django.db import models
from django.conf import settings

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    hod = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'HOD'},
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    staff = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'STAFF'},
        related_name='subjects'
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'STUDENT'},
        related_name='enrolled_subjects',
        blank=True
    )

    def __str__(self):
        return f"{self.name} ({self.code})"
