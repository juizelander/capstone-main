import os
import sys
import django
from django.core.management import call_command

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
django.setup()

# Output file
output_file = 'db.json'

print(f"Exporting data to {output_file} with UTF-8 encoding...")
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        call_command('dumpdata', exclude=['auth.permission', 'contenttypes', 'sessions'], stdout=f)
    print("Success! Data exported.")
except Exception as e:
    print(f"Error: {e}")
