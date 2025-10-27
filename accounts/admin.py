from django.contrib import admin
from .models import Student, Admin  # or whatever your role models are

admin.site.register(Student)
admin.site.register(Admin)
