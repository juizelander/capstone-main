import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
django.setup()

from accounts.models import ApplicationDocument
from home.models import Application

with open('db_check_result.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total ApplicationDocuments: {ApplicationDocument.objects.count()}\n")
    
    last_app = Application.objects.order_by('app_id').last()
    if last_app:
        f.write(f"Last Application ID: {last_app.app_id} by {last_app.student}\n")
        docs = last_app.documents.all()
        f.write(f"Documents linked to Last App: {docs.count()}\n")
        for doc in docs:
            f.write(f" - {doc.file.name} (ID: {doc.id}, Uploaded: {doc.uploaded_at})\n")
    else:
        f.write("No applications found.\n")
