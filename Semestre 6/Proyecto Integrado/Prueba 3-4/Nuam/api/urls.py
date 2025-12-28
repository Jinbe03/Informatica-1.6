from django.urls import path
from . import views
from .views import admin_desbloquear_usuario


urlpatterns = [

    path('', views.login_view, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('panel/', views.index, name='index'),
    path('calificacion/guardar/', views.guardar_calificacion, name='guardar_calificacion'),
    path('calificacion/eliminar/<int:id>/', views.eliminar_calificacion, name='eliminar_calificacion'),
    path('usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('usuarios/guardar/', views.guardar_usuario, name='guardar_usuario'),
    path('usuarios/eliminar/<int:perfil_id>/', views.eliminar_usuario_panel, name='eliminar_usuario'),
    path('auditoria/fragment/', views.auditoria_fragment, name='auditoria_fragment'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
    path('import/excel/', views.import_excel, name='import_excel'),
    path("admin/desbloquear/", admin_desbloquear_usuario, name="admin_desbloquear"),
    path('admin/desbloqueo/', views.admin_desbloqueo, name='admin_desbloqueo'),
    path("dashboard/desbloqueo/", views.admin_desbloqueo, name="admin_desbloqueo"),
]
