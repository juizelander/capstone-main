import os
import sys
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
import django
django.setup()

from home.models import Program
from accounts.models import Application, Student

students = Student.objects.all()
student = students.first()
if getattr(student, 'id', None):
    student_id = student.id
elif getattr(student, 'student_id', None):
    student_id = student.student_id
else:
    student_id = student.pk

print(f"Testing with student {student_id}")

programs = Program.objects.all()
for p in programs:
    user_app = Application.objects.filter(student_id=student_id, program=p).first()
    print(f"Program: {p.program_name}, max_slots={p.max_slots}, App={user_app}")
