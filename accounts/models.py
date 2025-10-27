from django.db import models


class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    admin_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.admin_name


class Student(models.Model):
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
    status = models.CharField(max_length=50, default='active')
    doc_submitted = models.FileField(upload_to='documents/', blank=True, null=True)

    def __str__(self):
        return self.username
# Create your models here.
