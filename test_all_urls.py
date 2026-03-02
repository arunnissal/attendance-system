import os
import django
import sys
from django.test.client import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_attendance.settings')
django.setup()

User = get_user_model()
client = Client()

urls_to_test = [
    ('login', None, None), # url_name, kwargs, expected_status
    ('hod_dashboard', None, 'HOD'),
    ('staff_dashboard', None, 'STAFF'),
    ('staff_records', None, 'STAFF'),
    ('student_dashboard', None, 'STUDENT'),
    ('student_scan', None, 'STUDENT'),
]

# Ensure users exist
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')

for role in ['HOD', 'STAFF', 'STUDENT']:
    if not User.objects.filter(username=f'test_{role.lower()}').exists():
        User.objects.create_user(f'test_{role.lower()}', password='password', role=role)

errors = []

for url_name, kwargs, role in urls_to_test:
    if role:
        client.login(username=f'test_{role.lower()}', password='password')
    else:
        client.logout()

    try:
        url = reverse(url_name, kwargs=kwargs)
        response = client.get(url)
        if response.status_code >= 400 and response.status_code != 403: # Allow 403 if it's role based redirect/deny, but we expect 200 mostly
             errors.append(f"Error {response.status_code} on {url_name}")
             print(f"FAILED: {url_name} returned {response.status_code}")
             print(response.content.decode('utf-8')[:500])
        else:
            print(f"SUCCESS: {url_name} rendered successfully (Status {response.status_code})")
    except Exception as e:
        errors.append(f"Crash on {url_name}: {str(e)}")
        print(f"CRASH: {url_name} - {str(e)}")

if errors:
    print("\n--- SUMMARY OF ERRORS ---")
    for err in errors:
        print(err)
    sys.exit(1)
else:
    print("\nAll tested URLs rendered without crashing!")
    sys.exit(0)
