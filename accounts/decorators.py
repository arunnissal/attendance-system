from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def role_required(*roles):
    def check_role(user):
        if not user.is_authenticated:
            return False
        if user.is_superuser or user.role in roles:
            return True
        raise PermissionDenied
    return user_passes_test(check_role, login_url='/accounts/login/')

def admin_required():
    return role_required('ADMIN')

def hod_required():
    return role_required('HOD')

def staff_required():
    return role_required('STAFF')

def student_required():
    return role_required('STUDENT')
