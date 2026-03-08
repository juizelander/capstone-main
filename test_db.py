import os
import sys
import django

sys.path.append('/Users/michaeljamesfeliminiano/Documents/capstone-main')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
django.setup()

from home.models import Program
from accounts.models import Application, Student

print(f"Total Programs: {Program.objects.count()}")
for p in Program.objects.all():
    print(f"- {p.program_name} (ID: {p.program_id})")

print(f"Total Applications: {Application.objects.count()}")
for app in Application.objects.all():
    print(f"- App ID: {app.app_id}, Student: {app.student_id}, Program: {app.program.program_name}, Status: {app.requirement_status}")
