from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_superuser or user.role == 'ADMIN':
            return reverse_lazy('admin:index')
        elif user.role == 'HOD':
            return reverse_lazy('hod_dashboard')
        elif user.role == 'STAFF':
            return reverse_lazy('staff_dashboard')
        elif user.role == 'STUDENT':
            return reverse_lazy('student_dashboard')
        return reverse_lazy('login')
