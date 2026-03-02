# Smart Attendance System using QR Technology

This is a modern, full-stack smart attendance system built with Django. It features a role-based access control system for Admin, HoD, Staff, and Students. The UI is built using purely HTML/CSS with a Glassmorphism design system.

## Features
- **Role-Based Access:** 
  - **Admin**: Has full access via Django Admin dashboard.
  - **HoD**: Can create staff, students, subjects and assign. Views overall stats.
  - **Staff**: Can select subject, start a dynamic session (QR/OTP valid for 30s only, updates continuously) and view live student attendance. Can export previous records as CSV.
  - **Student**: Dashboard with Chart.js attendance chart. Can manually input 6-digit session OTP or scan QR to mark attendance within validity period.
- **Security Check:** Verifies student role, valid subject enrollment, and expiry time.

## Requirements
- Python 3.10+
- Django 5.x
- qrcode (for Python QR gen)
- pillow
- Chart.js (Loaded via CDN in frontend)

## Installation Guide

1. Clone setup to your local drive.
2. Initialize and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install django qrcode pillow
   ```
4. Perform migrations:
   ```bash
   python manage.py makemigrations accounts core attendance dashboard
   python manage.py migrate
   ```
5. Create Superuser (Admin):
   ```bash
   python manage.py createsuperuser
   ```
6. Start the server:
   ```bash
   python manage.py runserver
   ```

## Usage & Default Test Accounts
I have pre-generated default accounts for every role so you can test the application immediately without creating new users:

- **Admin Login:** `admin` / `admin`
- **HoD Login:** `hod1` / `hod123`
- **Staff Login:** `staff1` / `staff123`
- **Student Login:** `student1` / `student123`

The HoD is assigned to the **Computer Science** department. `staff1` and `student1` are pre-assigned to **CS101 Intro to CS**.

### Flow
- Go to `http://127.0.0.1:8000/accounts/login/`
- Login as Admin, configure HoD role.
- Login as HoD, create Staff and Student accounts.
- Staff creates a live Session.
- Student logs in to another browser, goes to `Scan QR` and inputs the generated 6 digit OTP.

_This application adheres to best practices utilizing standard Django Class Based Views, Functional Views, context processors, and pure CSS for aesthetics._
