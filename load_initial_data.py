import os
import django
import sys

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command

def load_data():
    User = get_user_model()
    
    # Check if we are running in production (RENDER env var is usually present)
    # If the database already has users, we should NOT blindly overwrite it 
    # unless FORCE_DB_SYNC is explicitly set.
    if os.environ.get('RENDER') and not os.environ.get('FORCE_DB_SYNC'):
        if User.objects.exists():
            print("Database already contains data.")
            print("Skipping loaddata to prevent overwriting production data on server restart.")
            print("To force sync, set FORCE_DB_SYNC=1 in Render Environment Variables.")
            sys.exit(0)

    print("Loading datadump.json...")
    try:
        call_command('loaddata', 'datadump.json')
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    load_data()
