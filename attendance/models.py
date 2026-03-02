from django.db import models
from django.conf import settings
from core.models import Subject
import uuid

class Session(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'STAFF'}
    )
    date = models.DateField(auto_now_add=True)
    start_time = models.DateTimeField(auto_now_add=True)
    expiry_time = models.DateTimeField()
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    otp = models.CharField(max_length=6)
    
    @property
    def is_active(self):
        from django.utils import timezone
        return timezone.now() <= self.expiry_time

    def __str__(self):
        return f"{self.subject.name} - {self.date} - {self.start_time.strftime('%H:%M')}"

class Attendance(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'STUDENT'}
    )
    time_marked = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.session.subject.name} - {self.time_marked.strftime('%H:%M')}"
