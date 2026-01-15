import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
django.setup()

from accounts.models import Popup
from django.utils import timezone

with open('debug_output.txt', 'w') as f:
    f.write("--- Active Popups Debug ---\n")
    now = timezone.now()
    f.write(f"Current server time: {now}\n")

    try:
        popups = Popup.objects.all()
        f.write(f"Total Popups: {popups.count()}\n")

        for p in popups:
            f.write(f"ID: {p.id} | Title: {p.title} | Active: {p.is_active} | Expires: {p.expires_at}\n")
            
            is_active_flag = p.is_active
            not_expired = (p.expires_at is None) or (p.expires_at > now)
            
            f.write(f"  -> Eligible for student? Active={is_active_flag}, NotExpired={not_expired}\n")
            if is_active_flag and not_expired:
                f.write("  -> SHOULD BE VISIBLE\n")
            else:
                f.write("  -> HIDDEN\n")

    except Exception as e:
        f.write(f"Error querying popups: {e}\n")
