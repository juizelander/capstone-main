import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
django.setup()

from accounts.models import ApplicationDocument, Application
from home.models import Application as HomeApplication

print("--- Debugging Application Documents ---")

# Check counts
print(f"Total ApplicationDocuments: {ApplicationDocument.objects.count()}")

# List recent documents
print("\nRecent Documents:")
for doc in ApplicationDocument.objects.order_by('-uploaded_at')[:5]:
    print(f"ID: {doc.id}, App ID: {doc.application.app_id}, File: {doc.file.name}, Uploaded: {doc.uploaded_at}")

# Check recent applications
print("\nRecent Applications (Home Model):")
for app in HomeApplication.objects.order_by('-app_id')[:5]:
    try:
        doc_count = app.documents.count()
        print(f"App ID: {app.app_id}, Student: {app.student}, Program: {app.program}, Docs Linked: {doc_count}")
    except Exception as e:
        print(f"App ID: {app.app_id} - Error checking docs: {e}")
