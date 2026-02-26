from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.landing_page_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('register/', views.register_view, name='register'),
    
    # Admin API endpoints
    path('api/admin/stats/', views.admin_stats, name='admin_stats'),
    path('api/admin/change-password/', views.admin_change_password, name='admin_change_password'),
    path('api/admin/create-admin/', views.create_admin, name='create_admin'),
    
    # Popup management endpoints
    path('api/student/popups/', views.get_student_popups, name='get_student_popups'),
    path('api/student/popups/<int:popup_id>/mark-viewed/', views.mark_popup_viewed, name='mark_popup_viewed'),
    path('api/admin/popups/', views.get_popups, name='get_popups'),
    path('api/admin/popups/<int:popup_id>/', views.get_popup, name='get_popup'),
    path('api/admin/popups/create/', views.create_popup, name='create_popup'),
    path('api/admin/popups/<int:popup_id>/edit/', views.edit_popup, name='edit_popup'),
    path('api/admin/popups/<int:popup_id>/toggle/', views.toggle_popup, name='toggle_popup'),
    path('api/admin/popups/<int:popup_id>/delete/', views.delete_popup, name='delete_popup'),
    path('api/admin/reports/', views.generate_report, name='generate_report'),
    
    # Student application management endpoints
    path('api/admin/student-applications/', views.get_student_applications, name='get_student_applications'),
    path('api/admin/student-applications/<int:student_id>/approve/', views.approve_student, name='approve_student'),
    path('api/admin/student-applications/<int:student_id>/reject/', views.reject_student, name='reject_student'),
    path('api/admin/students/<int:student_id>/toggle/', views.toggle_student_status, name='toggle_student_status'),
    path('api/admin/students/<int:student_id>/edit/', views.edit_student, name='edit_student'),
    path('api/admin/students/<int:student_id>/delete/', views.delete_student, name='delete_student'),
    path('api/admin/students/<int:student_id>/renew/', views.renew_student, name='renew_student'),
    # path('api/programs/create/', views.create_program, name='create_program'),
    path('create_program/', views.create_program, name='create_program'),
    path('api/applications/create/', views.create_student_application, name='create_student_application'),
    path('api/student/applications/', views.get_my_applications, name='get_my_applications'),
    path('api/applications/<int:application_id>/mark-remarks-viewed/', views.mark_remarks_viewed, name='mark_remarks_viewed'),
    
    # Student profile API
    path('api/student/profile/update/', views.update_student_profile, name='update_student_profile'),
    path('student/change-password/', views.student_change_password, name='student_change_password'),
    
    # Student Document endpoints
    path('api/student/documents/', views.get_student_documents, name='get_student_documents'),
    path('api/student/documents/upload/', views.upload_student_document, name='upload_student_document'),
    path('api/student/documents/<int:doc_id>/delete/', views.delete_student_document, name='delete_student_document'),
    
    # Program application management endpoints
    path('api/admin/program-applications/', views.get_program_applications, name='get_program_applications'),
    path('api/admin/program-applications/<int:application_id>/approve/', views.approve_program_application, name='approve_program_application'),
    path('api/admin/program-applications/<int:application_id>/reject/', views.reject_program_application, name='reject_program_application'),
    path('api/admin/programs/<int:program_id>/applicants/', views.get_program_applicants_by_program, name='get_program_applicants_by_program'),
    
    # Messaging and Ticketing API
    path('api/messages/', views.get_messages, name='get_messages'),
    path('api/messages/<int:message_id>/read/', views.mark_message_read, name='mark_message_read'),
    path('api/messages/send/', views.send_message, name='send_message'),
    path('api/admin/messages/send-system/', views.admin_send_system_message, name='admin_send_system_message'),
    path('api/admin/messages/send-email/', views.admin_send_email, name='admin_send_email'),
    path('api/admin/messages/send-batch/', views.admin_send_batch_message, name='admin_send_batch_message'),
    
    # Chart data endpoints
    path('api/admin/charts/application-trends/', views.get_application_trends, name='get_application_trends'),
    path('api/admin/charts/student-statistics/', views.get_student_statistics, name='get_student_statistics'),
    
    # Student Voucher and Admin Receipt
    path('student/voucher/<int:application_id>/', views.student_voucher_view, name='student_voucher'),
    path('admin-receipt/<int:application_id>/', views.admin_receipt_view, name='admin_receipt'),
    path('api/admin/students/<int:student_id>/documents/', views.admin_get_student_documents, name='admin_get_student_documents'),
]