from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import Student, Popup
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Processes student account expiries (warns at 4 months, inactive at 5 months, deletes at 6 months)'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        
        # We need to find students who were approved
        # A 4 month warning is 120 days
        # A 5 month deactivation is 150 days
        # A 6 month deletion is 180 days
        
        warning_threshold = now - timedelta(days=120)
        inactive_threshold = now - timedelta(days=150)
        delete_threshold = now - timedelta(days=180)

        students = Student.objects.filter(approved_at__isnull=False)
        
        warnings_sent = 0
        accounts_deactivated = 0
        accounts_deleted = 0

        for student in students:
            # 6 MONTHS: Delete
            if student.approved_at <= delete_threshold:
                self.stdout.write(f"Deleting student {student.username} (Approved: {student.approved_at})")
                student.delete()
                accounts_deleted += 1
                continue
                
            # 5 MONTHS: Disable account
            if student.approved_at <= inactive_threshold and student.status == 'active':
                self.stdout.write(f"Deactivating student {student.username} (Approved: {student.approved_at})")
                student.status = 'inactive'
                student.save()
                accounts_deactivated += 1
                continue
                
            # 4 MONTHS: Warn via Email and System Popup
            if student.approved_at <= warning_threshold and student.warning_sent_at is None and student.status == 'active':
                self.stdout.write(f"Sending warning to student {student.username} (Approved: {student.approved_at})")
                
                # Send Email
                subject = 'Account Expiration Warning'
                message = f'Dear {student.first_name},\n\nYour account has been active for 4 months. As per our archiving policy, your account will be disabled in 1 month (at 5 months) and deleted in 2 months (at 6 months). Please contact the administration if you need to renew your account.\n\nThank you.'
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [student.email], fail_silently=True)
                except Exception as e:
                    self.stderr.write(f"Failed to send email to {student.email}: {e}")

                # Create Popup Notification
                popup = Popup.objects.create(
                    title='Account Expiration Warning',
                    message='Your account will expire soon according to our 6-month archiving policy. It will be disabled next month and deleted the month after. Please contact admin to renew.',
                    popup_type='warning',
                    is_active=True,
                )
                popup.seen_by.add(student)
                
                # Update warning sent timestamp
                student.warning_sent_at = now
                student.save()
                warnings_sent += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully processed accounts: {warnings_sent} warned, {accounts_deactivated} deactivated, {accounts_deleted} deleted.'))
