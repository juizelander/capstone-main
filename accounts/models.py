from django.db import models
from django.utils import timezone


class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.admin_name


class Student(models.Model):
    BARANGAY_CHOICES = [
        ('Aningway-Sacatihan', 'Aningway-Sacatihan'),
        ('Asinan (Poblacion)', 'Asinan (Poblacion)'),
        ('Asinan Proper', 'Asinan Proper'),
        ('Baraca-Camachile (Poblacion)', 'Baraca-Camachile (Poblacion)'),
        ('Batiawan', 'Batiawan'),
        ('Calapacuan', 'Calapacuan'),
        ('Calapandayan (Poblacion)', 'Calapandayan (Poblacion)'),
        ('Cawag', 'Cawag'),
        ('Ilwas (Poblacion)', 'Ilwas (Poblacion)'),
        ('Mangan-Vaca', 'Mangan-Vaca'),
        ('Matain', 'Matain'),
        ('Naugsol', 'Naugsol'),
        ('Pamatawan', 'Pamatawan'),
        ('San Isidro', 'San Isidro'),
        ('Santo Tomas', 'Santo Tomas'),
        ('Wawandue (Poblacion)', 'Wawandue (Poblacion)'),
    ]

    STUDENT_TYPE_CHOICES = [
        ('Junior High School', 'Junior High School'),
        ('Senior High School', 'Senior High School'),
        ('Undergraduate', 'Undergraduate'),
        ("Master's", "Master's"),
        ('Doctoral', 'Doctoral'),
        ('Board Exam', 'Board Exam'),
    ]

    student_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bday = models.DateField()
    address = models.TextField()
    barangay = models.CharField(max_length=50, choices=BARANGAY_CHOICES, blank=True, null=True)
    student_type = models.CharField(max_length=50, choices=STUDENT_TYPE_CHOICES, blank=True, null=True)
    contact_num = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    program_and_yr = models.CharField(max_length=100, blank=True, null=True)
    scholarship = models.CharField(max_length=100, blank=True, null=True)
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], default='Male')
    password = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='pending')
    doc_submitted = models.FileField(upload_to='documents/', blank=True, null=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username


class StudentDocument(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.student.username}"


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
    seen_by = models.ManyToManyField(Student, blank=True, related_name='seen_popups')
    
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
    is_remarks_viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application {self.app_id} - {self.student.username}"


class ApplicationDocument(models.Model):
    application = models.ForeignKey('home.Application', on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='application_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Doc for App {self.application.app_id}"


class Message(models.Model):
    SENDER_TYPES = [
        ('admin', 'Admin'),
        ('student', 'Student'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='messages')
    admin = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_messages')
    
    sender_type = models.CharField(max_length=10, choices=SENDER_TYPES)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender_type.capitalize()} Message: {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"
