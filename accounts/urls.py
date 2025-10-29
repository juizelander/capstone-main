from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.login_view, name='login'),  # Landing page
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('register/', views.register_view, name='register'),
    
    # Admin API endpoints
    path('api/admin/stats/', views.admin_stats, name='admin_stats'),
    
    # Popup management endpoints
    path('api/admin/popups/', views.get_popups, name='get_popups'),
    path('api/admin/popups/<int:popup_id>/', views.get_popup, name='get_popup'),
    path('api/admin/popups/create/', views.create_popup, name='create_popup'),
    path('api/admin/popups/<int:popup_id>/edit/', views.edit_popup, name='edit_popup'),
    path('api/admin/popups/<int:popup_id>/toggle/', views.toggle_popup, name='toggle_popup'),
    path('api/admin/popups/<int:popup_id>/delete/', views.delete_popup, name='delete_popup'),
    
    # Student application management endpoints
    path('api/admin/student-applications/', views.get_student_applications, name='get_student_applications'),
    path('api/admin/student-applications/<int:student_id>/approve/', views.approve_student, name='approve_student'),
    path('api/admin/student-applications/<int:student_id>/reject/', views.reject_student, name='reject_student'),
    # path('api/programs/create/', views.create_program, name='create_program'),
    path('create_program/', views.create_program, name='create_program'),
    path('api/applications/create/', views.create_student_application, name='create_student_application'),
    
    # Program application management endpoints
    path('api/admin/program-applications/', views.get_program_applications, name='get_program_applications'),
    path('api/admin/program-applications/<int:application_id>/approve/', views.approve_program_application, name='approve_program_application'),
    path('api/admin/program-applications/<int:application_id>/reject/', views.reject_program_application, name='reject_program_application'),
    
    # Chart data endpoints
    path('api/admin/charts/application-trends/', views.get_application_trends, name='get_application_trends'),
    path('api/admin/charts/student-statistics/', views.get_student_statistics, name='get_student_statistics'),

]