from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .models import Session, Attendance
from core.models import Subject
from accounts.decorators import staff_required, student_required
import random
import uuid
import qrcode
from io import BytesIO
import base64

@staff_required()
def start_session(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Check if an active session already exists for this subject and staff today
        session = Session.objects.filter(
            subject=subject, 
            staff=request.user, 
            date=timezone.now().date(),
            expiry_time__gt=timezone.now()
        ).first()

        if not session:
            # Create a new session
            otp = str(random.randint(100000, 999999))
            expiry_time = timezone.now() + timezone.timedelta(seconds=60)
            session = Session.objects.create(
                subject=subject,
                staff=request.user,
                expiry_time=expiry_time,
                otp=otp
            )
        
        return JsonResponse({'status': 'success', 'session_id': session.id})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@staff_required()
def regenerate_session(request, session_id):
    session = get_object_or_404(Session, id=session_id, staff=request.user)
    
    # Update token and OTP
    session.token = uuid.uuid4()
    session.otp = str(random.randint(100000, 999999))
    session.expiry_time = timezone.now() + timezone.timedelta(seconds=60)
    session.save()
    
    # Generate QR Code base64 image
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(f"urn:smart_attendance:session:{str(session.token)}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Get live attendance list
    attendances = Attendance.objects.filter(session=session).select_related('student')
    attendance_data = [{
        'name': att.student.get_full_name() or att.student.username,
        'roll_number': att.student.username,
        'time_marked': att.time_marked.strftime("%H:%M:%S")
    } for att in attendances]
    
    total_students = session.subject.students.count()
    present_count = attendances.count()

    return JsonResponse({
        'status': 'success',
        'otp': session.otp,
        'qr_base64': qr_base64,
        'expiry_time': session.expiry_time.isoformat(),
        'attendances': attendance_data,
        'present_count': present_count,
        'total_count': total_students
    })

@student_required()
def mark_attendance(request):
    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()
        token = request.POST.get('token', '').strip()
        
        # Cleanup token if scanned via QR
        if token and token.startswith('urn:smart_attendance:session:'):
            token = token.split('urn:smart_attendance:session:')[1]
            
        session = None
        if otp:
            session = Session.objects.filter(otp=otp, expiry_time__gte=timezone.now()).first()
        elif token:
            session = Session.objects.filter(token=token, expiry_time__gte=timezone.now()).first()
            
        if not session:
            return JsonResponse({'status': 'error', 'message': 'Session expired or invalid.'})
            
        if not session.subject.students.filter(id=request.user.id).exists():
            return JsonResponse({'status': 'error', 'message': 'You are not enrolled in this subject.'})
            
        att, created = Attendance.objects.get_or_create(
            session=session,
            student=request.user
        )
        
        if created:
            return JsonResponse({'status': 'success', 'message': 'Attendance marked successfully.'})
        else:
            return JsonResponse({'status': 'info', 'message': 'Attendance already marked.'})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
