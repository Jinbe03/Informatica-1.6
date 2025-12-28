from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    return HttpResponse("Bienvenido al sistema de gestion de turnos del Carwash")

def home(request):
    return render(request, "turnos/home.html")

def reservas(request):
    return render(request, "turnos/reservas.html")

def lista_precios(request):
    return render(request, 'turnos/lista-precios.html')
