import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Admin, Student

users = User.objects.all()
print(f"Total Users: {len(users)}")
for u in users:
    role = "Unknown"
    if Admin.objects.filter(user=u).exists():
        role = "Admin"
    elif Student.objects.filter(user=u).exists():
        role = "Student"
    print(f"Username: {u.username}, Role: {role}, Is Staff: {u.is_staff}")
