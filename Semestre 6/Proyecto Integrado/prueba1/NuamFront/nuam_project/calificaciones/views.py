from django.shortcuts import render, redirect
from .models import Calificacion
from .mongo_client import collection
from datetime import datetime

def log_auditoria(usuario, accion, empresa=None):
    collection.insert_one({
        "usuario": usuario,
        "accion": accion,
        "empresa": empresa,
        "fecha": datetime.utcnow()
    })

def index(request):
    calificaciones = Calificacion.objects.all()
    return render(request, 'calificaciones/index.html', {'calificaciones': calificaciones})

def guardar_calificacion(request):
    if request.method == "POST":
        empresa = request.POST.get("empresa")
        periodo = request.POST.get("periodo")
        tipo = request.POST.get("tipo")
        calificacion = request.POST.get("calificacion")
        fuente = request.POST.get("fuente")
        observaciones = request.POST.get("observaciones")

        # Guardar en PostgreSQL
        Calificacion.objects.create(
            empresa=empresa,
            periodo=periodo,
            tipo=tipo,
            calificacion=calificacion,
            fuente=fuente,
            observaciones=observaciones
        )

        # Guardar log en MongoDB
        collection.insert_one({
            "usuario": "admin",
            "accion": "Agregó calificación",
            "empresa": empresa,
            "fecha": datetime.utcnow()
        })

    return redirect('index')
