from django.contrib.auth.decorators import login_required
from accounts.decorators import hod_required, staff_required, student_required, admin_required
from django.contrib.auth import get_user_model
from core.models import Subject, Department
from attendance.models import Session, Attendance
from django.db.models import Count, Q
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

User = get_user_model()

@login_required
@admin_required()
def admin_dashboard(request):
    departments = Department.objects.all()
    hods = User.objects.filter(role='HOD')
    
    total_departments = departments.count()
    total_hods = hods.count()
    
    context = {
        'departments': departments,
        'hods': hods,
        'total_departments': total_departments,
        'total_hods': total_hods
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
@admin_required()
def create_hod(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username {username} already exists.")
        else:
            User.objects.create_user(
                username=username, 
                password=password, 
                first_name=first_name, 
                last_name=last_name, 
                email=email,
                role='HOD'
            )
            messages.success(request, f"HoD user {username} created successfully.")
            
    return redirect('admin_dashboard')

@login_required
@admin_required()
def create_department(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if Department.objects.filter(name=name).exists():
            messages.error(request, f"Department {name} already exists.")
        else:
            Department.objects.create(name=name)
            messages.success(request, f"Department {name} created successfully.")
            
    return redirect('admin_dashboard')

@login_required
@admin_required()
def assign_hod(request):
    if request.method == 'POST':
        department_id = request.POST.get('department_id')
        hod_id = request.POST.get('hod_id')
        
        department = get_object_or_404(Department, id=department_id)
        if not hod_id:
            department.hod = None
            department.save()
            messages.success(request, f"HoD unassigned from {department.name}.")
        else:
            hod = get_object_or_404(User, id=hod_id, role='HOD')
            
            # Remove this HoD from any other department first (OneToOne field logic usually handles this, but explicitly handling it is safer)
            Department.objects.filter(hod=hod).update(hod=None)
            
            department.hod = hod
            department.save()
            messages.success(request, f"{hod.username} assigned as HoD of {department.name}.")
            
    return redirect('admin_dashboard')

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

import json
from django.db.models import Count

@login_required
@hod_required()
def manage_staff(request):
    try:
        department = request.user.department
    except Department.DoesNotExist:
        messages.error(request, "No department assigned to your profile.")
        return redirect('hod_dashboard')

    staff_users = User.objects.filter(role='STAFF', subjects__department=department).distinct()
    
    staff_data = []
    for staff in staff_users:
        subjects_assigned = staff.subjects.filter(department=department)
        total_sessions = Session.objects.filter(staff=staff, subject__department=department).count()
        staff_data.append({
            'user': staff,
            'subjects': subjects_assigned,
            'total_sessions': total_sessions
        })
        
    context = {'staff_data': staff_data, 'department': department}
    return render(request, 'dashboard/manage_staff.html', context)

@login_required
@hod_required()
def manage_students(request):
    try:
        department = request.user.department
    except Department.DoesNotExist:
        messages.error(request, "No department assigned.")
        return redirect('hod_dashboard')

    q = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    students = User.objects.filter(role='STUDENT', enrolled_subjects__department=department).distinct()

    if q:
        students = students.filter(
            Q(first_name__icontains=q) | 
            Q(last_name__icontains=q) | 
            Q(username__icontains=q)
        )

    student_data = []
    for student in students:
        enrolled = student.enrolled_subjects.filter(department=department)
        total_sessions = Session.objects.filter(subject__in=enrolled).count()
        attended = Attendance.objects.filter(student=student, session__subject__department=department).count()
        
        percentage = 0
        if total_sessions > 0:
            percentage = round((attended / total_sessions) * 100, 2)
            
        status = 'Safe' if percentage >= 75 else 'Shortage'
        
        if status_filter and status_filter != status:
            continue
            
        student_data.append({
            'user': student,
            'percentage': percentage,
            'status': status,
            'department_name': department.name
        })

    context = {
        'student_data': student_data,
        'department': department,
        'q': q,
        'status_filter': status_filter
    }
    return render(request, 'dashboard/manage_students.html', context)

@login_required
@hod_required()
def student_detail(request, student_id):
    try:
        department = request.user.department
    except Department.DoesNotExist:
        return redirect('hod_dashboard')
        
    student = get_object_or_404(User, id=student_id, role='STUDENT', enrolled_subjects__department=department)
    enrolled_subjects = student.enrolled_subjects.filter(department=department)
    
    subject_details = []
    chart_labels = []
    chart_attended = []
    chart_absent = []
    
    for sub in enrolled_subjects:
        total = Session.objects.filter(subject=sub).count()
        attended = Attendance.objects.filter(student=student, session__subject=sub).count()
        absent = total - attended
        percentage = round((attended/total)*100, 2) if total > 0 else 0
        
        subject_details.append({
            'subject': sub,
            'total': total,
            'attended': attended,
            'absent': absent,
            'percentage': percentage
        })
        chart_labels.append(sub.code)
        chart_attended.append(attended)
        chart_absent.append(absent)
        
    context = {
        'student': student,
        'subject_details': subject_details,
        'chart_labels': json.dumps(chart_labels),
        'chart_attended': json.dumps(chart_attended),
        'chart_absent': json.dumps(chart_absent),
    }
    return render(request, 'dashboard/student_detail.html', context)

@login_required
@hod_required()
def edit_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        
        if user.role == 'STUDENT':
            new_username = request.POST.get('username')
            if new_username and not User.objects.filter(username=new_username).exclude(id=user.id).exists():
                user.username = new_username
        user.save()
        messages.success(request, f"User {user.username} updated successfully.")
        
        return redirect('manage_staff' if user.role == 'STAFF' else 'manage_students')
    return redirect('hod_dashboard')

@login_required
@hod_required()
def reset_password(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        new_password = request.POST.get('password')
        if new_password:
            user.set_password(new_password)
            user.save()
            messages.success(request, f"Password reset for {user.username} successfully.")
        
        return redirect('manage_staff' if user.role == 'STAFF' else 'manage_students')
    return redirect('hod_dashboard')

@login_required
@hod_required()
def delete_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        role = user.role
        user.delete()
        messages.success(request, "User deleted successfully.")
        
        return redirect('manage_staff' if role == 'STAFF' else 'manage_students')
    return redirect('hod_dashboard')
