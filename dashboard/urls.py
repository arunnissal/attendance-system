from django.urls import path
from . import views

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/create-hod/', views.create_hod, name='create_hod'),
    path('admin-dashboard/create-department/', views.create_department, name='create_department'),
    path('admin-dashboard/assign-hod/', views.assign_hod, name='assign_hod'),
    
    path('hod/', views.hod_dashboard, name='hod_dashboard'),
    path('hod/departments/', views.hod_dashboard, name='hod_departments'), # Placeholder
    path('hod/manage-staff/', views.manage_staff, name='manage_staff'),
    path('hod/manage-students/', views.manage_students, name='manage_students'),
    path('hod/student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('hod/user/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('hod/user/<int:user_id>/reset-password/', views.reset_password, name='reset_password'),
    path('hod/user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/records/', views.staff_records, name='staff_records'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('student/scan/', views.student_scan, name='student_scan'),
]
