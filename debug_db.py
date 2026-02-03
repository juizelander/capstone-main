import os
import django
import sys

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
django.setup()

from django.apps import apps
from django.db import connection

print("--- INSPECTING MODELS ---")
app_models = []
for model in apps.get_models():
    if model.__name__ == 'Application':
        print(f"Found Application model: {model} in app '{model._meta.app_label}' table '{model._meta.db_table}'")
        app_models.append(model)
        
print("\n--- INSPECTING DATA ---")
for model in app_models:
    print(f"\nData for {model._meta.app_label}.Application:")
    count = model.objects.count()
    print(f"  Total Count: {count}")
    if count > 0:
        for obj in model.objects.all():
            # Try to get fields safely
            status = getattr(obj, 'requirement_status', 'N/A')
            print(f"    ID: {obj.pk}, Status: '{status}' (Type: {type(status)})")
            
            # Check for whitespace
            if isinstance(status, str) and status != status.strip():
                 print(f"    WARNING: Status has whitespace! '{status}'")

print("\n--- CHECKING TABLES IN DB ---")
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables found:", [t[0] for t in tables if 'application' in t[0] or 'Application' in t[0]])
