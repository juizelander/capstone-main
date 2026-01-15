from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count
from django.db.models.functions import TruncDay, TruncMonth
import json
from .models import Admin, Student, Popup
from django.db import models
from home.models import Program, Application
from django.http import HttpResponse


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Check if user is Admin
        admin_user = Admin.objects.filter(admin_name=username, password=password).first()
        if admin_user:
            request.session['user_role'] = 'admin'
            request.session['user_id'] = admin_user.admin_id

            return redirect('accounts:admin_dashboard')
        # Check if user is Student
        student_user = Student.objects.filter(username=username, password=password).first()
        if student_user:
            # Check if student is approved
            if student_user.status == 'active':
                request.session['user_role'] = 'student'
                request.session['user_id'] = student_user.pk
                request.session['username'] = student_user.username
                return redirect('accounts:student_dashboard')
            elif student_user.status == 'pending':
                return render(request, 'accounts/login.html', {'error': 'Your account is pending approval. Please wait for admin approval.'})
            elif student_user.status == 'rejected':
                return render(request, 'accounts/login.html', {'error': 'Your account has been rejected. Please contact the administrator.'})

        # Invalid credentials
        return render(request, 'accounts/login.html', {'error': 'Invalid username or password'})

    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        bday = request.POST.get('bday')  # <-- capture birthday
        address = request.POST.get('address')
        contact_num = request.POST.get('contact_num')
        program_and_yr = request.POST.get('program_and_yr')
        document = request.FILES.get('document')
        status='pending'  # Set initial status as pending

        # create student
        student = Student.objects.create(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            bday=bday,  # <-- include birthday here
            address=address,
            contact_num=contact_num,
            program_and_yr=program_and_yr,
            doc_submitted=document,
            status='pending'  # Set initial status as pending
        )
        student.save()
        messages.success(request, "Registration successful! Your account is pending admin approval. You will be notified once approved.")
        return redirect('accounts:login')

    return render(request, 'accounts/register.html')

def approve_student(request, student_id):
    if request.method == 'POST':
        student = get_object_or_404(Student, pk=student_id)
        action = request.POST.get('action')
        
        if action == 'approve':
            student.status = 'active'
        elif action == 'reject':
            student.status = 'rejected'
            
        student.save()
        return JsonResponse({'status': 'success'})


def admin_dashboard(request):
    admin_id = request.session.get('user_id')
    if not admin_id:
        return redirect('login')
    admin = Admin.objects.get(admin_id=admin_id)
    return render(request, 'accounts/admin_dashboard.html', {'admin': admin})


def student_dashboard(request):
    student_id = request.session.get('user_id')
    if not student_id:
        return redirect('login')
    student = get_object_or_404(Student, pk=student_id)
    return render(request, 'accounts/student_dashboard.html', {'student': student})

def logout_view(request):
    request.session.flush()  # clears all session data
    return redirect('accounts:login')


def create_program(request):
    print("🟢 create_program reached:", request.method)
    if request.method == 'POST':
        program_name = request.POST.get('program_name')
        requirements = request.POST.get('requirements')
        print("📦 POST DATA:", request.POST)

        if not program_name:
            messages.error(request, "Program name is required.")
            return redirect('accounts:admin_dashboard')

        Program.objects.create(program_name=program_name, requirements=requirements)
        messages.success(request, f"Program '{program_name}' created successfully!")
        print("✅ Program created:", program_name)
        return redirect('accounts:admin_dashboard')

    messages.error(request, "Invalid request.")
    print("❌ Invalid request method")
    return redirect('accounts:admin_dashboard')


@csrf_exempt
@require_http_methods(["POST"])
def create_student_application(request):
    """Student submits application to a program"""
    student_id = request.session.get('user_id')
    if not student_id:
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=401)

    try:
        program_id = request.POST.get('program') or request.POST.get('program_id')
        motivation = request.POST.get('motivation', '')

        if not program_id:
            return JsonResponse({'success': False, 'error': 'Program is required'}, status=400)

        # Get entities
        student = get_object_or_404(Student, pk=student_id)
        program = get_object_or_404(Program, program_id=program_id)

        app = Application.objects.create(
            student=student,
            program=program,
            requirement_status='submitted',
            remarks=motivation,
        )

        return JsonResponse({'success': True, 'application_id': app.app_id})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
# Popup Management Views
def admin_stats(request):
    """Get admin dashboard statistics"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        total_students = Student.objects.filter(status='active').count()
        active_popups = Popup.objects.filter(is_active=True).count()
        pending_applications = Student.objects.filter(status='pending').count()
        total_programs = Program.objects.count()
        
        return JsonResponse({
            'total_students': total_students,
            'active_popups': active_popups,
            'pending_applications': pending_applications,
            'total_programs': total_programs
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_popups(request):
    """Get all popups for the admin"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        popups = Popup.objects.all().order_by('-created_at')
        popup_data = []
        
        for popup in popups:
            popup_data.append({
                'id': popup.id,
                'title': popup.title,
                'message': popup.message,
                'popup_type': popup.popup_type,
                'is_active': popup.is_active,
                'created_at': popup.created_at.isoformat(),
                'updated_at': popup.updated_at.isoformat(),
                'expires_at': popup.expires_at.isoformat() if popup.expires_at else None
            })
        
        return JsonResponse({'popups': popup_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_popup(request, popup_id):
    """Get a specific popup"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        popup = get_object_or_404(Popup, id=popup_id)
        return JsonResponse({
            'id': popup.id,
            'title': popup.title,
            'message': popup.message,
            'popup_type': popup.popup_type,
            'is_active': popup.is_active,
            'created_at': popup.created_at.isoformat(),
            'updated_at': popup.updated_at.isoformat(),
            'expires_at': popup.expires_at.isoformat() if popup.expires_at else None
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_student_popups(request):
    """Get active popups for students"""
    student_id = request.session.get('user_id')
    if not student_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        now = timezone.now()
        # Fetch active popups that haven't expired
        popups = Popup.objects.filter(
            is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        ).order_by('-created_at')
        
        popup_data = []
        for popup in popups:
            popup_data.append({
                'id': popup.id,
                'title': popup.title,
                'message': popup.message,
                'popup_type': popup.popup_type,
                'created_at': popup.created_at.isoformat()
            })
        
        return JsonResponse({'popups': popup_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_popup(request):
    """Create a new popup"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        data = json.loads(request.body)
        
        # Parse expires_at if provided
        expires_at = None
        if data.get('expires_at'):
            expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
        
        popup = Popup.objects.create(
            title=data['title'],
            message=data['message'],
            popup_type=data['popup_type'],
            is_active=data.get('is_active', True),
            expires_at=expires_at
        )
        
        return JsonResponse({
            'success': True,
            'popup_id': popup.id,
            'message': 'Popup created successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def edit_popup(request, popup_id):
    """Edit an existing popup"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        popup = get_object_or_404(Popup, id=popup_id)
        data = json.loads(request.body)
        
        # Parse expires_at if provided
        expires_at = None
        if data.get('expires_at'):
            expires_at = datetime.fromisoformat(data['expires_at'].replace('Z', '+00:00'))
        
        popup.title = data['title']
        popup.message = data['message']
        popup.popup_type = data['popup_type']
        popup.is_active = data.get('is_active', True)
        popup.expires_at = expires_at
        popup.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Popup updated successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def toggle_popup(request, popup_id):
    """Toggle popup active status"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        popup = get_object_or_404(Popup, id=popup_id)
        popup.is_active = not popup.is_active
        popup.save()
        
        return JsonResponse({
            'success': True,
            'is_active': popup.is_active,
            'message': f'Popup {"activated" if popup.is_active else "deactivated"} successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def delete_popup(request, popup_id):
    """Delete a popup"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        popup = get_object_or_404(Popup, id=popup_id)
        popup.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Popup deleted successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Student Application Management Views
def get_student_applications(request):
    """Get all student applications for admin review"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        students = Student.objects.all().order_by('-student_id')
        application_data = []
        
        for student in students:
            application_data.append({
                'id': student.pk,
                'username': student.username,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'email': student.email,
                'bday': student.bday.isoformat(),
                'address': student.address,
                'contact_num': student.contact_num,
                'program_and_yr': student.program_and_yr,
                'status': student.status,
                'doc_submitted': student.doc_submitted.url if student.doc_submitted else None,
                'created_at': student.created_at.isoformat() if student.created_at else None
            })
        
        return JsonResponse({'applications': application_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def approve_student(request, student_id):
    """Approve a student application"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        student = get_object_or_404(Student, pk=student_id)
        student.status = 'active'
        student.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Student application approved successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def reject_student(request, student_id):
    """Reject a student application"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        student = get_object_or_404(Student, pk=student_id)
        student.status = 'rejected'
        student.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Student application rejected successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Program Application Management Views
def get_program_applications(request):
    """Get all program applications for admin review"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        # First check if we have any applications
        total_applications = Application.objects.count()
        print(f"Debug: Total applications found: {total_applications}")
        
        if total_applications == 0:
            return JsonResponse({'applications': []})
        
        # Get applications with related data
        applications = Application.objects.select_related('student', 'program').all().order_by('-app_id')
        application_data = []
        
        for app in applications:
            try:
                # Safely access student data
                student_data = {
                    'username': getattr(app.student, 'username', 'Unknown'),
                    'first_name': getattr(app.student, 'first_name', 'Unknown'),
                    'last_name': getattr(app.student, 'last_name', 'Unknown'),
                    'email': getattr(app.student, 'email', 'Unknown'),
                }
                
                # Safely access program data
                program_data = {
                    'program_name': getattr(app.program, 'program_name', 'Unknown Program'),
                }
                
                application_data.append({
                    'app_id': app.app_id,
                    'student': student_data,
                    'program': program_data,
                    'requirement_status': getattr(app, 'requirement_status', 'unknown'),
                    'remarks': getattr(app, 'remarks', ''),
                    'created_at': getattr(app, 'created_at', None)
                })
                
            except Exception as e:
                print(f"Debug: Error processing application {getattr(app, 'app_id', 'unknown')}: {str(e)}")
                continue
        
        return JsonResponse({'applications': application_data})
        
    except Exception as e:
        print(f"Debug: Error in get_program_applications: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': f'Database error: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def approve_program_application(request, application_id):
    """Approve a program application"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        application = get_object_or_404(Application, app_id=application_id)
        application.requirement_status = 'approved'
        application.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Program application approved successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def reject_program_application(request, application_id):
    """Reject a program application"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        application = get_object_or_404(Application, app_id=application_id)
        application.requirement_status = 'rejected'
        application.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Program application rejected successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# Chart Data API Views
def get_application_trends(request):
    """Get application trends data for charts"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        period = request.GET.get('period', '30')  # Default to 30 days
        days = int(period)
        
        # Calculate start date
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Get application data grouped by day
        applications_by_day = Student.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        # Create a complete date range with counts
        date_counts = {}
        for item in applications_by_day:
            date_counts[item['day']] = item['count']
        
        # Generate labels and data arrays
        labels = []
        data = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime('%b %d')
            labels.append(date_str)
            data.append(date_counts.get(current_date, 0))
            current_date += timedelta(days=1)
        
        return JsonResponse({
            'labels': labels,
            'data': data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_student_statistics(request):
    """Get student statistics data for charts"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        chart_type = request.GET.get('type', 'status')
        
        if chart_type == 'status':
            # Get students by status
            status_data = Student.objects.values('status').annotate(count=Count('id'))
            
            labels = []
            data = []
            colors = []
            
            status_colors = {
                'active': 'rgba(102, 126, 234, 0.8)',
                'pending': 'rgba(243, 156, 18, 0.8)',
                'rejected': 'rgba(231, 76, 60, 0.8)'
            }
            
            for item in status_data:
                labels.append(item['status'].title())
                data.append(item['count'])
                colors.append(status_colors.get(item['status'], 'rgba(102, 126, 234, 0.8)'))
            
        elif chart_type == 'program':
            # Get students by program
            program_data = Student.objects.values('program_and_yr').annotate(count=Count('id')).order_by('-count')[:10]
            
            labels = []
            data = []
            colors = [
                'rgba(102, 126, 234, 0.8)',
                'rgba(118, 75, 162, 0.8)',
                'rgba(39, 174, 96, 0.8)',
                'rgba(243, 156, 18, 0.8)',
                'rgba(231, 76, 60, 0.8)',
                'rgba(52, 152, 219, 0.8)',
                'rgba(155, 89, 182, 0.8)',
                'rgba(46, 204, 113, 0.8)',
                'rgba(230, 126, 34, 0.8)',
                'rgba(231, 76, 60, 0.8)'
            ]
            
            for i, item in enumerate(program_data):
                labels.append(item['program_and_yr'])
                data.append(item['count'])
            
            colors = colors[:len(labels)]
            
        elif chart_type == 'monthly':
            # Get monthly registrations for the last 6 months
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=180)  # 6 months
            
            monthly_data = Student.objects.filter(
                created_at__date__gte=start_date
            ).extra(
                select={'month': 'strftime("%Y-%m", created_at)'}
            ).values('month').annotate(count=Count('id')).order_by('month')
            
            labels = []
            data = []
            
            for item in monthly_data:
                # Format month label
                month_date = datetime.strptime(item['month'], '%Y-%m')
                labels.append(month_date.strftime('%b'))
                data.append(item['count'])
        
        return JsonResponse({
            'labels': labels,
            'data': data,
            'colors': colors if chart_type in ['status', 'program'] else None
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

