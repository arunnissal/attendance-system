from django.urls import path
from . import views

urlpatterns = [
    path('hod/', views.hod_dashboard, name='hod_dashboard'),
    path('hod/departments/', views.hod_dashboard, name='hod_departments'), # Placeholder
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/records/', views.staff_records, name='staff_records'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/scan/', views.student_scan, name='student_scan'),
]
