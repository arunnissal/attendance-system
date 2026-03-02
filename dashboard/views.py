from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import hod_required, staff_required, student_required
from django.contrib.auth import get_user_model
from core.models import Subject, Department
from attendance.models import Session, Attendance
from django.db.models import Count, Q
from django.contrib import messages

User = get_user_model()

@login_required
@hod_required()
def hod_dashboard(request):
    try:
        department = request.user.department
    except Department.DoesNotExist:
        department = None
        
    staff_users = User.objects.filter(role='STAFF')
    student_users = User.objects.filter(role='STUDENT')
    subjects = Subject.objects.all()
    if department:
        subjects = subjects.filter(department=department)

    # Forms processing
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create_user':
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            role = request.POST.get('role') # STAFF or STUDENT
            password = request.POST.get('password')
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name, role=role)
                messages.success(request, f"{role} {username} created successfully.")
            else:
                messages.error(request, f"Username {username} already exists.")
            return redirect('hod_dashboard')
            
        elif action == 'create_subject' and department:
            name = request.POST.get('name')
            code = request.POST.get('code')
            if not Subject.objects.filter(code=code).exists():
                subject = Subject.objects.create(name=name, code=code, department=department)
                messages.success(request, f"Subject {name} created successfully.")
            else:
                messages.error(request, f"Subject code {code} already exists.")
            return redirect('hod_dashboard')
            
        elif action == 'assign_staff':
            subject_id = request.POST.get('subject_id')
            staff_id = request.POST.get('staff_id')
            subject = get_object_or_404(Subject, id=subject_id)
            staff = get_object_or_404(User, id=staff_id, role='STAFF')
            subject.staff.add(staff)
            messages.success(request, f"{staff.username} assigned to {subject.name}.")
            return redirect('hod_dashboard')

    # Dashboard Statistics
    total_sessions = Session.objects.filter(subject__in=subjects).count()
    
    # Subject wise attendance basic metric
    subject_stats = []
    for sub in subjects:
        sub_sessions = Session.objects.filter(subject=sub).count()
        if sub_sessions > 0:
            att_count = Attendance.objects.filter(session__subject=sub).count()
            # Approximation logic: Total possible attendance = total_sessions * students enrolled
            enrolled = sub.students.count()
            if enrolled > 0:
                percentage = (att_count / (sub_sessions * enrolled)) * 100
                subject_stats.append({'subject': sub, 'percentage': round(percentage, 2)})

    context = {
        'department': department,
        'staff_users': staff_users,
        'student_users': student_users,
        'subjects': subjects,
        'total_sessions': total_sessions,
        'subject_stats': subject_stats,
    }
    return render(request, 'dashboard/hod_dashboard.html', context)

@login_required
@staff_required()
def staff_dashboard(request):
    subjects = request.user.subjects.all()
    context = {
        'subjects': subjects
    }
    return render(request, 'dashboard/staff_dashboard.html', context)

@login_required
@staff_required()
def staff_records(request):
    import csv
    from django.http import HttpResponse
    
    sessions = Session.objects.filter(staff=request.user).order_by('-date', '-start_time')
    
    # Download logic
    if 'download' in request.GET:
        session_id = request.GET.get('session_id')
        format_type = request.GET.get('download')
        
        session = get_object_or_404(Session, id=session_id, staff=request.user)
        attendances = Attendance.objects.filter(session=session)
        
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="attendance_{session.subject.code}_{session.date}.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Roll Number', 'Name', 'Time Marked'])
            for att in attendances:
                writer.writerow([att.student.username, att.student.get_full_name(), att.time_marked.strftime("%H:%M:%S")])
            return response
            
    context = {
        'sessions': sessions
    }
    return render(request, 'dashboard/staff_records.html', context)

@login_required
@student_required()
def student_dashboard(request):
    import json
    user = request.user
    
    enrolled_subjects = user.enrolled_subjects.all()
    total_sessions_conducted = Session.objects.filter(subject__in=enrolled_subjects).count()
    total_attended = Attendance.objects.filter(student=user).count()
    
    attendance_percentage = 0
    if total_sessions_conducted > 0:
        attendance_percentage = round((total_attended / total_sessions_conducted) * 100, 2)
        
    subject_labels = []
    subject_data = []
    for sub in enrolled_subjects:
        sub_sessions = Session.objects.filter(subject=sub).count()
        if sub_sessions > 0:
            att = Attendance.objects.filter(student=user, session__subject=sub).count()
            subject_labels.append(sub.code)
            subject_data.append(round((att/sub_sessions)*100, 2))
            
    recent_attendances = Attendance.objects.filter(student=user).order_by('-time_marked')[:10]

    context = {
        'total_sessions': total_sessions_conducted,
        'total_attended': total_attended,
        'attendance_percentage': attendance_percentage,
        'chart_labels': json.dumps(subject_labels),
        'chart_data': json.dumps(subject_data),
        'recent_attendances': recent_attendances
    }
    return render(request, 'dashboard/student_dashboard.html', context)

@login_required
@student_required()
def student_scan(request):
    return render(request, 'dashboard/student_scan.html')


