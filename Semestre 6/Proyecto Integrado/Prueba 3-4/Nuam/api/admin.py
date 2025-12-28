from django.contrib import admin
from .models import PerfilUsuario, Calificacion
from .models import Auditoria

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol')  #
    search_fields = ('user__username', 'rol') 
    list_filter = ('rol',)  


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'periodo', 'tipo', 'calificacion', 'fuente')
    search_fields = ('empresa', 'tipo', 'fuente')
    list_filter = ('tipo', 'periodo')

@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('user', 'accion', 'fecha')
    search_fields = ('user__username', 'accion')
    list_filter = ('accion', 'fecha')
    ordering = ('-fecha',)

    readonly_fields = ('user', 'accion', 'fecha')

    fieldsets = (
        ('Registro de Auditoría', {
            'fields': ('user', 'accion', 'fecha')
        }),
    )