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
from .models import Admin, Student, Popup, StudentDocument, ApplicationDocument
from django.db import models
from home.models import Program, Application
from django.http import HttpResponse
import csv
import os
from django.conf import settings
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


def landing_page_view(request):
    try:
        # Fetch active programs
        active_programs = Program.objects.filter(is_active=True)
    except Exception:
        # Fallback if migration hasn't run yet or other error
        active_programs = []
    
    return render(request, 'accounts/landing_page.html', {'active_programs': active_programs})


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
            elif student_user.status == 'inactive':
                return render(request, 'accounts/login.html', {'error': 'Account disabled'})

        # Invalid credentials
        return render(request, 'accounts/login.html', {'error': 'Invalid username or password'})

    return render(request, 'accounts/login.html')

import re

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Password Validation
        if not re.match(r'^(?=.*\d)(?=.*[A-Z]).{8,}$', password):
            messages.error(request, "Password must be at least 8 characters long, contain at least one capital letter and one number.")
            return render(request, 'accounts/register.html')

        if password != confirm_password:
             messages.error(request, "Passwords do not match.")
             return render(request, 'accounts/register.html')
        
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        # Check for duplicates
        if Student.objects.filter(email=email).exists():
            messages.error(request, "Email address is already in use.")
            return render(request, 'accounts/register.html')
            
        if Student.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'accounts/register.html')

        bday = request.POST.get('bday')  # <-- capture birthday
        address = request.POST.get('address')
        contact_num = request.POST.get('contact_num')
        program_and_yr = request.POST.get('program_and_yr')
        sex = request.POST.get('sex')
        documents = request.FILES.getlist('document') # Capture multiple files
        
        # Determine initial status
        status='pending'  

        # Create student (save first document to doc_submitted for backward compatibility if needed)
        first_doc = documents[0] if documents else None

        student = Student.objects.create(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            bday=bday,  
            address=address,
            contact_num=contact_num,
            program_and_yr=program_and_yr,
            sex=sex,
            doc_submitted=first_doc,
            status='pending' 
        )
        
        # Save all documents
        for doc in documents:
            StudentDocument.objects.create(student=student, file=doc)

        student.save()
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
    programs = Program.objects.all()

    return render(request, 'accounts/admin_dashboard.html', {'admin': admin, 'programs': programs})


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

        program_type = request.POST.get('program_type')

        if not program_name:
            messages.error(request, "Program name is required.")
            return redirect('accounts:admin_dashboard')

        Program.objects.create(program_name=program_name, requirements=requirements, program_type=program_type)
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

        # Handle multiple supporting documents
        documents = request.FILES.getlist('supporting_docs')
        for doc in documents:
            ApplicationDocument.objects.create(application=app, file=doc)

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
        pending_student_registrations = Student.objects.filter(status='pending').count()
        pending_program_applications = Application.objects.filter(requirement_status='submitted').count()
        total_programs = Program.objects.count()
        
        return JsonResponse({
            'total_students': total_students,
            'active_popups': active_popups,
            'pending_applications': pending_student_registrations, # Keeping for backward compatibility
            'pending_student_registrations': pending_student_registrations,
            'pending_program_applications': pending_program_applications,
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
        student = get_object_or_404(Student, pk=student_id)

        # Fetch active popups that haven't expired and not seen by student
        popups = Popup.objects.filter(
            is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) | models.Q(expires_at__gt=now)
        ).exclude(
            seen_by=student
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
def mark_popup_viewed(request, popup_id):
    """Mark a popup as viewed by the student"""
    student_id = request.session.get('user_id')
    if not student_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        popup = get_object_or_404(Popup, id=popup_id)
        student = get_object_or_404(Student, pk=student_id)
        
        popup.seen_by.add(student)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


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


@csrf_exempt
@require_http_methods(["POST"])
def toggle_student_status(request, student_id):
    """Toggle student active status"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        student = get_object_or_404(Student, pk=student_id)
        
        # If currently active, deactivate (set to inactive/suspended)
        # Using 'inactive' as the status for deactivated students
        if student.status == 'active':
            student.status = 'inactive'
            action = 'deactivated'
        else:
            # If rejected, pending, or inactive, set to active
            student.status = 'active'
            action = 'activated'
            
        student.save()
        
        return JsonResponse({
            'success': True,
            'status': student.status,
            'message': f'Student {action} successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def edit_student(request, student_id):
    """Edit student details"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        student = get_object_or_404(Student, pk=student_id)
        # Handle both JSON and Form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        student.first_name = data.get('first_name', student.first_name)
        student.last_name = data.get('last_name', student.last_name)
        student.username = data.get('username', student.username)
        student.email = data.get('email', student.email)
        student.contact_num = data.get('contact_num', student.contact_num)
        student.address = data.get('address', student.address)
        student.program_and_yr = data.get('program_and_yr', student.program_and_yr)
        
        # Only allow changing status if provided
        if 'status' in data:
            student.status = data['status']

        student.save()

        return JsonResponse({
            'success': True,
            'message': 'Student details updated successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def delete_student(request, student_id):
    """Delete a student account"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        student = get_object_or_404(Student, pk=student_id)
        username = student.username
        student.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Student {username} deleted successfully'
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
                    'doc_submitted': app.student.doc_submitted.url if app.student.doc_submitted else None,
                }
                
                # Fetch documents for this application
                documents_list = []
                app_docs = app.documents.all()
                for doc in app_docs:
                     documents_list.append({
                        'url': doc.file.url, 
                        'name': doc.file.name.split('/')[-1]
                     })
                
                # Safely access program data
                program_data = {
                    'program_name': getattr(app.program, 'program_name', 'Unknown Program'),
                }
                
                application_data.append({
                    'app_id': app.app_id,
                    'student': student_data,
                    'program': program_data,
                    'documents': documents_list,
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
        data = json.loads(request.body)
        remarks = data.get('remarks', '')

        application = get_object_or_404(Application, app_id=application_id)
        application.requirement_status = 'approved'
        application.remarks = remarks
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
        data = json.loads(request.body)
        remarks = data.get('remarks', '')

        application = get_object_or_404(Application, app_id=application_id)
        application.requirement_status = 'rejected'
        application.remarks = remarks
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
        applications_by_day = Application.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(count=Count('app_id')).order_by('day')
        
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


@csrf_exempt
def get_my_applications(request):
    """Get logged-in student's applications"""
    student_id = request.session.get('user_id')
    if not student_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        student = get_object_or_404(Student, pk=student_id)
        applications = Application.objects.filter(student=student).select_related('program').order_by('-created_at')
        
        app_list = []
        for app in applications:
            app_list.append({
                'app_id': app.app_id,
                'program_name': app.program.program_name,
                'requirement_status': app.requirement_status,
                'remarks': app.remarks,
                'is_remarks_viewed': app.is_remarks_viewed,
                'created_at': app.created_at.isoformat() if app.created_at else None
            })
            
        return JsonResponse({'applications': app_list})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def mark_remarks_viewed(request, application_id):
    """Mark application remarks as viewed"""
    student_id = request.session.get('user_id')
    if not student_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
        
    try:
        # Verify the application belongs to this student
        app = get_object_or_404(Application, app_id=application_id, student__pk=student_id)
        
        app.is_remarks_viewed = True
        app.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def student_voucher_view(request, application_id):
    """View to generic voucher for accepted students"""
    student_id = request.session.get('user_id')
    if not student_id:
        return redirect('accounts:login')
    
    student = get_object_or_404(Student, pk=student_id)
    application = get_object_or_404(Application, app_id=application_id, student=student)
    
    # Check if application is approved
    if application.requirement_status != 'approved':
        # You might want to show a message or redirect
        messages.error(request, "Voucher is only available for approved applications.")
        return redirect('accounts:student_dashboard')
        
    context = {
        'student': student,
        'application': application,
        'program': application.program,
        'now': timezone.now()
    }
    return render(request, 'accounts/student_voucher.html', context)


def generate_report(request):
    """Generate and export reports"""
    admin_id = request.session.get('user_id')
    if not admin_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    try:
        report_type = request.GET.get('type')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        status = request.GET.get('status')
        program_id = request.GET.get('program')
        export_csv = request.GET.get('export') == 'true'

        data = []
        filename = f"report_{report_type}_{datetime.now().strftime('%Y%m%d')}"

        if report_type == 'students':
            # Base query
            query = Student.objects.all().order_by('-created_at')

            # Filters
            if start_date:
                query = query.filter(created_at__date__gte=start_date)
            if end_date:
                query = query.filter(created_at__date__lte=end_date)
            if status and status != 'all':
                query = query.filter(status=status)
            # Program filter for students is based on 'program_and_yr' string
            # This might be tricky if it's just free text in Student model
            # But let's try if the user passes something matching
            
            # For data creation
            header = ['Student ID', 'Username', 'First Name', 'Last Name', 'Email', 'Program', 'Status', 'Date Joined']
            
            for s in query:
                data.append({
                    'id': s.student_id,
                    'username': s.username,
                    'first_name': s.first_name,
                    'last_name': s.last_name,
                    'email': s.email,
                    'program': s.program_and_yr,
                    'status': s.status,
                    'created_at': s.created_at.strftime('%Y-%m-%d') if s.created_at else 'N/A'
                })

        elif report_type == 'applications':
            # Base query
            query = Application.objects.select_related('student', 'program').all().order_by('-created_at')

            # Filters
            if start_date:
                query = query.filter(created_at__date__gte=start_date)
            if end_date:
                query = query.filter(created_at__date__lte=end_date)
            if status and status != 'all':
                query = query.filter(requirement_status=status)
            if program_id and program_id != 'all':
                query = query.filter(program_id=program_id)

            header = ['App ID', 'Student', 'Program', 'Status', 'Date Submitted']
            
            for app in query:
                data.append({
                    'id': app.app_id,
                    'student': f"{app.student.first_name} {app.student.last_name}",
                    'program': app.program.program_name,
                    'status': app.requirement_status,
                    'created_at': app.created_at.strftime('%Y-%m-%d') if app.created_at else 'N/A'
                })
        
        else:
             return JsonResponse({'error': 'Invalid report type'}, status=400)

        # Handle CSV Export
        if export_csv:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'

            writer = csv.writer(response)
            writer.writerow(header)

            if report_type == 'students':
                 for row in data:
                    writer.writerow([row['id'], row['username'], row['first_name'], row['last_name'], row['email'], row['program'], row['status'], row['created_at']])
            else:
                for row in data:
                    writer.writerow([row['id'], row['student'], row['program'], row['status'], row['created_at']])

            return response
        
        # Handle Word Export
        # Handle Word Export
        if request.GET.get('export') == 'word':
            document = Document()
            
            # Set Font to Calibri
            style = document.styles['Normal']
            font = style.font
            font.name = 'Calibri'
            font.size = Pt(11) # Default size, usually 11 for Calibri
            
            # Adjust Margins
            section = document.sections[0]
            section.top_margin = Inches(0.5)
            section.left_margin = Inches(0.5)
            section.right_margin = Inches(0.5)
            section.bottom_margin = Inches(0.5)

            
            # Header Setup
            header_section = section.header
            header_section.is_linked_to_previous = False
            
            # Use a table for header layout to align Logo Left and Title Center
            # 3 columns: Left (Logo), Center (Title), Right (Balance/Empty)
            htable = header_section.add_table(1, 3, width=Inches(7.5)) # Width = 8.5 - 0.5 - 0.5
            htable.autofit = False
            htable.columns[0].width = Inches(1.5)
            htable.columns[1].width = Inches(4.5)
            htable.columns[2].width = Inches(1.5)
            
            # Cell 0: Logo
            cell0 = htable.cell(0, 0)
            # Remove default empty paragraph if needed, or just use it
            p0 = cell0.paragraphs[0]
            p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
            logo_path = os.path.join(settings.BASE_DIR, 'accounts', 'static', 'accounts', 'subic_seal.png')
            if os.path.exists(logo_path):
                run0 = p0.add_run()
                run0.add_picture(logo_path, height=Inches(0.8)) # Changed to height
            
            # Cell 1: Title
            cell1 = htable.cell(0, 1)
            p1 = cell1.paragraphs[0]
            p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run1 = p1.add_run('ScholarSync Subic')
            run1.bold = True
            run1.font.size = Pt(22) 
            
            # Cell 2: Second Logo
            cell2 = htable.cell(0, 2)
            p2 = cell2.paragraphs[0]
            p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
            logo2_path = os.path.join(settings.BASE_DIR, 'accounts', 'static', 'accounts', 'scholarsync_logo.png')
            if os.path.exists(logo2_path):
                run2 = p2.add_run()
                run2.add_picture(logo2_path, height=Inches(0.8)) # Changed to height
            
            # Remove the default empty paragraph in the header if it causes spacing issues?
            # No, standard is just adding it. But usually header starts with one P. 
            # Let's remove the default paragraph to avoid top padding.
            if len(header_section.paragraphs) > 0:
                header_section.paragraphs[0]._element.getparent().remove(header_section.paragraphs[0]._element)

            # Add a paragraph for the separator line
            border_paragraph = header_section.add_paragraph()
            border_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            border_paragraph.paragraph_format.space_after = Pt(0)
            
            # Apply bottom border to this paragraph using OXML
            p = border_paragraph._p
            pPr = p.get_or_add_pPr()
            pBdr = OxmlElement('w:pBdr')
            bottom = OxmlElement('w:bottom')
            bottom.set(qn('w:val'), 'single')
            bottom.set(qn('w:sz'), '6')  # 1/8 pt, so 6 is 3/4 pt. Thin line.
            bottom.set(qn('w:space'), '1')
            bottom.set(qn('w:color'), 'CCCCCC') # Gray color
            pBdr.append(bottom)
            pPr.append(pBdr)

            
            # Subtitle (Body)
            # Subtitle (Body)
            subtitle = document.add_paragraph()
            subtitle_run = subtitle.add_run(f'Report: {report_type.title()}')
            subtitle_run.bold = True
            subtitle_run.underline = True
            subtitle_run.font.size = Pt(14)
            subtitle.alignment = WD_ALIGN_PARAGRAPH.LEFT
            subtitle.paragraph_format.space_after = Pt(6) # Small space before table
            
            # Spacer removed to bring closer to table
            
            # Filter headers for Word (Remove Email and Status)
            word_header = list(header)
            fields_to_remove = ['Email', 'Status']
            for field in fields_to_remove:
                if field in word_header:
                    word_header.remove(field)

            # Table
            table = document.add_table(rows=1, cols=len(word_header))
            table.style = 'Table Grid'
            
            # Helper function for shading
            def set_cell_background(cell, color_hex):
                tcPr = cell._tc.get_or_add_tcPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:val'), 'clear')
                shd.set(qn('w:color'), 'auto')
                shd.set(qn('w:fill'), color_hex)
                tcPr.append(shd)

            # Table Header
            hdr_cells = table.rows[0].cells
            for i, col_name in enumerate(word_header):
                cell = hdr_cells[i]
                set_cell_background(cell, '2E8B57') # Sea Green
                run = cell.paragraphs[0].add_run(col_name)
                run.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255) # White text
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Table Data
            rows_data = [] # Collect data first to iterate easily
            if report_type == 'students':
                for row in data:
                    rows_data.append([
                        str(row.get('id', '')),
                        str(row.get('username', '')),
                        str(row.get('first_name', '')),
                        str(row.get('last_name', '')),
                        str(row.get('program', '')),
                        str(row.get('created_at', ''))
                    ])
            else:
                for row in data:
                    rows_data.append([
                        str(row.get('id', '')),
                        str(row.get('student', '')),
                        str(row.get('program', '')),
                        str(row.get('created_at', ''))
                    ])

            for index, row_content in enumerate(rows_data):
                row_cells = table.add_row().cells
                is_even = (index % 2 == 0)
                bg_color = 'E8F5E9' if is_even else 'FFFFFF' # Light Green / White
                
                for i, text in enumerate(row_content):
                    cell = row_cells[i]
                    cell.text = text
                    # Apply background color
                    if is_even: # Only apply if not white (default)
                         set_cell_background(cell, bg_color)
            
            # Metadata (Below Table)
            document.add_paragraph() # Spacer
            meta = document.add_paragraph()
            meta.alignment = WD_ALIGN_PARAGRAPH.LEFT
            gen_run = meta.add_run(f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            gen_run.font.color.rgb = RGBColor(128, 128, 128) # Gray color
            
            if start_date:
                meta.add_run(f'Start Date: {start_date}\n')
            if end_date:
                meta.add_run(f'End Date: {end_date}')

            # Signature Section
            document.add_paragraph() # Spacer
            
            signature = document.add_paragraph()
            signature.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            sig_run = signature.add_run('Approved by: ____________________')
            sig_run.font.name = 'Calibri'
            sig_run.font.size = Pt(12)
            sig_run.font.color.rgb = RGBColor(0, 0, 0) # Black color explicitly
            
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            response['Content-Disposition'] = f'attachment; filename="{filename}.docx"'
            document.save(response)
            return response
        
        # Return JSON for table view
        return JsonResponse({'data': data})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
