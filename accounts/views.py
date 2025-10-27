from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Admin, Student

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Admin, Student

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Try Admin login
        admin = Admin.objects.filter(admin_name=username, password=password).first()
        if admin:
            request.session['user_role'] = 'admin'
            request.session['username'] = admin.admin_name
            return redirect('admin_dashboard')

        # Try Student login
        student = Student.objects.filter(username=username, password=password).first()
        if student:
            request.session['user_role'] = 'student'
            request.session['username'] = student.username
            return redirect('student_dashboard')

        # Invalid credentials
        messages.error(request, "Invalid username or password.")
    
    return render(request, 'accounts/login.html')

def register_view(request):
    return render(request, 'accounts/register.html')

def admin_dashboard(request):
    role = request.session.get('user_role')
    if role != 'admin':
        return redirect('login')
    return render(request, 'accounts/admin_dashboard.html')


def student_dashboard(request):
    role = request.session.get('user_role')
    if role != 'student':
        return redirect('login')
    return render(request, 'accounts/student_dashboard.html')


def logout_view(request):
    request.session.flush()  # clears all session data
    return redirect('login')
