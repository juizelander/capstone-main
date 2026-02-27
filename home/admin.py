from django.contrib import admin

from .models import Student, Application, Admin, Document, Program, Scholarship, Announcement

# Register all models so they appear in Django Admin
admin.site.register(Student)
admin.site.register(Application)
admin.site.register(Admin)
admin.site.register(Document)
admin.site.register(Program)
admin.site.register(Scholarship)
admin.site.register(Announcement)
