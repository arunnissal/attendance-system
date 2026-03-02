from django.urls import path
from . import views

urlpatterns = [
    path('start_session/', views.start_session, name='start_session'),
    path('regenerate_session/<int:session_id>/', views.regenerate_session, name='regenerate_session'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
]
