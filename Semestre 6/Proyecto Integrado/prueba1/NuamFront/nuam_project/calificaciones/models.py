from django.db import models

from django.db import models

class Calificacion(models.Model):
    empresa = models.CharField(max_length=200)
    periodo = models.DateField()
    tipo = models.CharField(max_length=20)
    calificacion = models.CharField(max_length=100)
    fuente = models.CharField(max_length=200, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
