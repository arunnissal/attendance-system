from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('HOD', 'HoD'),
        ('STAFF', 'Staff'),
        ('STUDENT', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"

    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser
        
    def is_hod(self):
        return self.role == 'HOD'
        
    def is_staff_member(self):
        return self.role == 'STAFF'
        
    def is_student(self):
        return self.role == 'STUDENT'
