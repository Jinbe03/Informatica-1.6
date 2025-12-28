from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('guardar/', views.guardar_calificacion, name='guardar_calificacion'),
]
