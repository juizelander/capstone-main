from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),  # Landing page
    path('logout/', views.logout_view, name='logout'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('register/', views.register_view, name='register'),
]