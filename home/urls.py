from django.urls import path
from . import views

urlpatterns = [
    # path('', views.home, name='home'),
    path('create_program/', views.create_program, name='create_program'),
    path('programs/', views.get_programs, name='get_programs'),
]
