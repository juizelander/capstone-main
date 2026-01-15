from accounts.models import Popup
from django.utils import timezone

print("--- Active Popups Debug ---")
now = timezone.now()
print(f"Current server time: {now}")

popups = Popup.objects.all()
print(f"Total Popups: {popups.count()}")

for p in popups:
    print(f"ID: {p.id} | Title: {p.title} | Active: {p.is_active} | Expires: {p.expires_at}")
    
    is_active_flag = p.is_active
    not_expired = (p.expires_at is None) or (p.expires_at > now)
    
    print(f"  -> Eligible for student? Active={is_active_flag}, NotExpired={not_expired}")
    if is_active_flag and not_expired:
        print("  -> SHOULD BE VISIBLE")
    else:
        print("  -> HIDDEN")
