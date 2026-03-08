
import os
import sys
import django

sys.path.append('.')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "capstone.settings")
django.setup()

from django.template.loader import get_template

try:
    t = get_template('accounts/student_dashboard.html')
    print("Template parsed successfully!")
except Exception as e:
    import traceback
    traceback.print_exc()
