from django.db import models


# -------------------------
# STUDENT TABLE
# -------------------------
class Student(models.Model):
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bday = models.DateField()
    address = models.CharField(max_length=255)
    contact_num = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    program_and_yr = models.CharField(max_length=100)
    scholarship = models.CharField(max_length=100, blank=True, null=True)  # Can link later via FK if needed
    password = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default='pending')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# -------------------------
# SCHOLARSHIP TABLE
# -------------------------
class Scholarship(models.Model):
    scholarsh_id = models.AutoField(primary_key=True)
    scholarsh_name = models.CharField(max_length=100)

    def __str__(self):
        return self.scholarsh_name


# -------------------------
# PROGRAMS TABLE
# -------------------------
class Program(models.Model):
    program_id = models.AutoField(primary_key=True)
    program_name = models.CharField(max_length=100)
    requirements = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.program_name


# -------------------------
# APPLICATION TABLE
# -------------------------
class Application(models.Model):
    app_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE, related_name='home_applications')
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    requirement_status = models.CharField(max_length=100)
    remarks = models.TextField(blank=True, null=True)
    notification = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Application {self.app_id} - {self.student}"


# -------------------------
# DOCUMENTS TABLE
# -------------------------
class Document(models.Model):
    doc_id = models.AutoField(primary_key=True)
    doc_name = models.CharField(max_length=100)
    file_path = models.FileField(upload_to='documents/')
    upload_date = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=50)
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE)

    def __str__(self):
        return self.doc_name


# -------------------------
# ADMIN TABLE
# -------------------------
class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.admin_name