from django.db import models
from django.utils import timezone


class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.admin_name


class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bday = models.DateField()
    address = models.TextField()
    contact_num = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    program_and_yr = models.CharField(max_length=100)
    scholarship = models.CharField(max_length=100, blank=True, null=True)
    password = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='pending')
    doc_submitted = models.FileField(upload_to='documents/', blank=True, null=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username


class Popup(models.Model):
    POPUP_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('success', 'Success'),
        ('error', 'Error'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    popup_type = models.CharField(max_length=20, choices=POPUP_TYPES, default='info')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.title


class Program(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    capacity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Program"
        verbose_name_plural = "Programs"

    def __str__(self):
        return self.title


class Application(models.Model):
    app_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='applications')
    program = models.ForeignKey('home.Program', on_delete=models.CASCADE, related_name='account_applications')
    requirement_status = models.CharField(max_length=100, default='submitted')
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application {self.app_id} - {self.student.username}"
