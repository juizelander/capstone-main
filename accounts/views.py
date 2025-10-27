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
            request.session['user_role'] = 'student'
            request.session['user_id'] = student_user.id
            request.session['username'] = student_user.username

            return redirect('accounts:student_dashboard')

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
            doc_submitted=document
        )
        student.save()
        messages.success(request, "Registration successful!")
        return redirect('accounts:login')

    return render(request, 'accounts/register.html')


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
    student = Student.objects.get(username=request.session['username'])
    return render(request, 'accounts/student_dashboard.html', {'student': student})

def logout_view(request):
    request.session.flush()  # clears all session data
    return redirect('accounts:login')

