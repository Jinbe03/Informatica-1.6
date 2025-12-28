from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('reservas/', views.reservas, name='reservas'),
    
]