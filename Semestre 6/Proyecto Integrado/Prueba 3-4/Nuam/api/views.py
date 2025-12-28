from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse

from .models import Calificacion, PerfilUsuario, Auditoria
from .forms import CalificacionForm, FiltroCalificacionForm

from decimal import Decimal

import pandas as pd
from xhtml2pdf import pisa

# ==========================================================
# LOGIN
# ==========================================================
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "api/login.html", {"error": "Correo no registrado."})

        perfil, creado = PerfilUsuario.objects.get_or_create(
            user=user,
            defaults={'rol': 'admin' if user.is_superuser else 'corredor'}
        )

        if perfil.esta_bloqueado():
            return render(request, "api/login.html", {
                "error": f"Cuenta bloqueada. Intente nuevamente a las {perfil.bloqueado_hasta.strftime('%H:%M:%S')}."
            })

        user_auth = authenticate(request, username=user.username, password=password)

        if user_auth:
            perfil.intentos_fallidos = 0
            perfil.bloqueado_hasta = None
            perfil.save()
            login(request, user_auth)
            Auditoria.objects.create(user=user, accion="Inicio de sesión exitoso")
            return redirect("index")
        else:
            perfil.intentos_fallidos += 1
            if perfil.intentos_fallidos >= 3:
                perfil.bloqueado_hasta = timezone.now() + timedelta(minutes=5)
                perfil.intentos_fallidos = 0
                perfil.save()
                Auditoria.objects.create(user=user, accion="Cuenta bloqueada por intentos fallidos")
                return render(request, "api/login.html", {"error": "Cuenta bloqueada 5 minutos por intentos fallidos."})
            perfil.save()
            Auditoria.objects.create(user=user, accion="Intento fallido de inicio de sesión")
            return render(request, "api/login.html", {"error": "Contraseña incorrecta."})

    return render(request, "api/login.html")


# ==========================================================
# LOGOUT
# ==========================================================
@login_required
def logout_view(request):
    Auditoria.objects.create(user=request.user, accion="Cerró sesión")
    logout(request)
    return redirect("login")


# ==========================================================
# PANEL PRINCIPAL
# ==========================================================
@login_required
def index(request):
    perfil = PerfilUsuario.objects.get(user=request.user)

    puede_crear = perfil.rol in ["admin", "corredor"]
    puede_editar = perfil.rol == "admin"
    puede_eliminar = perfil.rol == "admin"

    filtro_form = FiltroCalificacionForm(request.GET or None)
    calificaciones = Calificacion.objects.all()

    if filtro_form.is_valid():
        empresa = filtro_form.cleaned_data.get('empresa')
        tipo = filtro_form.cleaned_data.get('tipo')
        fecha_desde = filtro_form.cleaned_data.get('fecha_desde')
        fecha_hasta = filtro_form.cleaned_data.get('fecha_hasta')

        if empresa:
            from django.db.models.functions import Lower
            calificaciones = calificaciones.annotate(e=Lower('empresa')).filter(e__icontains=empresa.lower())
        if tipo:
            calificaciones = calificaciones.filter(tipo=tipo)
        if fecha_desde:
            calificaciones = calificaciones.filter(created_at__date__gte=fecha_desde)
        if fecha_hasta:
            calificaciones = calificaciones.filter(created_at__date__lte=fecha_hasta)

    calificaciones = calificaciones.order_by('-id')

    empresas = Calificacion.objects.values_list('empresa', flat=True).distinct().order_by('empresa')

    form = CalificacionForm()

    factores_principales = [
        ("factor_08", "Factor 08: Con crédito por IDPC generados a contar del 01.01.2017"),
        ("factor_09", "Factor 09: Con crédito por IDPC acumulados hasta el 31.12.2016"),
        ("factor_10", "Factor 10: Con derecho a crédito por pago IDPC voluntario"),
        ("factor_11", "Factor 11: Sin derecho a crédito"),
        ("factor_20", "Factor 20: Sin derecho a devolución"),
        ("factor_37", "Factor 37: Devolución de capital Art. 17 N°7 LIR"),
    ]

    factores_avanzados = [
        ("factor_12", "Factor 12: Impuesto 1ra categ. exento GL comp. con devolución"),
        ("factor_13", "Factor 13: Impuesto 1ra categ. afecto GL comp. sin devolución"),
        ("factor_14", "Factor 14: Impuesto 1ra categ. exento GL comp. sin devolución"),
        ("factor_15", "Factor 15: Impuesto. créditos por impuestos externos"),
        ("factor_16", "Factor 16: No constitutiva de renta acogida a impuesto"),
        ("factor_17", "Factor 17: No constitutiva de renta – devolución de capital Art. 17"),
        ("factor_18", "Factor 18: Rentas exentas de impuesto GC y/o impuesto adicional"),
        ("factor_19", "Factor 19: Ingreso no constitutivo de renta"),
        ("factor_21", "Factor 21: Con derecho a devolución"),
        ("factor_22", "Factor 22: Sin derecho a devolución"),
        ("factor_23", "Factor 23: Con derecho a devolución"),
        ("factor_24", "Factor 24: Sin derecho a devolución"),
        ("factor_25", "Factor 25: Con derecho a devolución"),
        ("factor_26", "Factor 26: Sin derecho a devolución"),
        ("factor_27", "Factor 27: Con derecho a devolución"),
        ("factor_28", "Factor 28: Crédito por IPE"),
        ("factor_29", "Factor 29: (reservado)"),
        ("factor_30", "Factor 30: Con derecho a devolución"),
        ("factor_31", "Factor 31: Sin derecho a devolución"),
        ("factor_32", "Factor 32: Con derecho a devolución"),
        ("factor_33", "Factor 33: Crédito por IPE"),
        ("factor_34", "Factor 34: Crédito por impuesto tasa adicional Ex Art. 21 LIR"),
        ("factor_35", "Factor 35: Tasa efectiva del crédito del FUT (TEF)"),
        ("factor_36", "Factor 36: Tasa efectiva del crédito del FUNT (TEX)"),
    ]

    return render(request, "api/index.html", {
        "perfil": perfil,
        "calificaciones": calificaciones,
        "form": form,
        "puede_crear": puede_crear,
        "puede_editar": puede_editar,
        "puede_eliminar": puede_eliminar,
        "filtro_form": filtro_form,
        "empresas": empresas,
        "factores_principales": factores_principales,
        "factores_avanzados": factores_avanzados,
    })


# ==========================================================
# CRUD DE CALIFICACIONES
# ==========================================================
@login_required
def guardar_calificacion(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol not in ["admin", "corredor"]:
        return redirect("index")

    if request.method == "POST":
        id = request.POST.get("id")

        # ===================== EDITAR =====================
        if id:
            calif = get_object_or_404(Calificacion, id=id)

            # ======= CAMPOS ANTIGUOS BÁSICOS =======
            old_basic = {
                "empresa": calif.empresa,
                "periodo": calif.periodo,
                "tipo": calif.tipo,
                "calificacion": calif.calificacion,
                "fuente": calif.fuente,
                "observaciones": calif.observaciones,
            }

            # ======= ACTUALIZAR CAMPOS BÁSICOS =======
            calif.empresa = request.POST.get("empresa")
            calif.periodo = request.POST.get("periodo")
            calif.tipo = request.POST.get("tipo")
            calif.calificacion = request.POST.get("calificacion")
            calif.fuente = request.POST.get("fuente")
            calif.observaciones = request.POST.get("observaciones")

            # ====== VALORES ANTIGUOS DE FACTORES ======
            old_factors = {}
            for campo in ['factor_08','factor_09','factor_10','factor_11','factor_20','factor_37']:
                old_factors[campo] = getattr(calif, campo)

            for n in range(12,37):
                c = f"factor_{n}"
                old_factors[c] = getattr(calif, c)

            # ======= ACTUALIZAR FACTORES =======
            for campo in ['factor_08','factor_09','factor_10','factor_11','factor_20','factor_37']:
                calif.__dict__[campo] = request.POST.get(campo, 0) or 0

            for n in range(12,37):
                c = f"factor_{n}"
                calif.__dict__[c] = request.POST.get(c, 0) or 0

            calif.save()

            # ===================== AUDITORÍA =====================
            cambios = []

            # 1️⃣ CAMBIOS EN CAMPOS BÁSICOS
            for campo, old_value in old_basic.items():
                new_value = getattr(calif, campo)
                if str(old_value) != str(new_value):
                    cambios.append(f"{campo}: {old_value} → {new_value}")

            # 2️⃣ CAMBIOS EN FACTORES (solo reales)
            for campo, old_value in old_factors.items():
                new_value = getattr(calif, campo)
                if Decimal(str(old_value)) != Decimal(str(new_value)):
                    cambios.append(f"{campo}: {old_value} → {new_value}")

            if cambios:
                Auditoria.objects.create(
                    user=request.user,
                    accion=f"Editó calificación ID {id}. Cambios: " + " | ".join(cambios)
                )
            else:
                Auditoria.objects.create(
                    user=request.user,
                    accion=f"Editó calificación ID {id} sin cambios."
                )

            return redirect("index")

        # ===================== CREAR =====================
        else:
            calif = Calificacion()
            calif.empresa = request.POST.get("empresa")
            calif.periodo = request.POST.get("periodo")
            calif.tipo = request.POST.get("tipo")
            calif.calificacion = request.POST.get("calificacion")
            calif.fuente = request.POST.get("fuente")
            calif.observaciones = request.POST.get("observaciones")

            for campo in ['factor_08','factor_09','factor_10','factor_11','factor_20','factor_37']:
                calif.__dict__[campo] = request.POST.get(campo, 0) or 0

            for n in range(12,37):
                c = f"factor_{n}"
                calif.__dict__[c] = request.POST.get(c, 0) or 0

            calif.save()

            Auditoria.objects.create(
                user=request.user,
                accion=f"Creó calificación ID {calif.id} para empresa {calif.empresa}"
            )

            return redirect("index")

    messages.error(request, "Error al guardar la calificación.")
    return redirect("index")


# ==========================================================
# ELIMINAR
# ==========================================================
@login_required
def eliminar_calificacion(request, id):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != "admin":
        return redirect("index")

    calif = get_object_or_404(Calificacion, id=id)
    calif.delete()
    Auditoria.objects.create(user=request.user, accion=f"Eliminó calificación ID {id}")
    return redirect("index")


# ==========================================================
# GESTIÓN DE USUARIOS
# ==========================================================
@login_required
def gestionar_usuarios(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != "admin":
        return redirect("index")
    usuarios = PerfilUsuario.objects.select_related("user").all()
    return render(request, "api/usuarios_gestion.html", {"usuarios": usuarios, "perfil": perfil})


@login_required
def guardar_usuario(request):
    perfil = PerfilUsuario.objects.get(user=request.user)
    if perfil.rol != "admin":
        return redirect("index")

    if request.method == "POST":
        usuario_id = request.POST.get("usuario_id")
        username = request.POST.get("username")
        email = request.POST.get("email")
        rol = request.POST.get("rol")

        # ------------------------
        # Validación: email único
        # ------------------------
        if usuario_id:
            # EDITando
            perfil_u = PerfilUsuario.objects.get(id=usuario_id)
            user = perfil_u.user
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, "El correo ingresado ya está registrado por otro usuario.")
                return redirect("gestionar_usuarios")
        else:
            # CREANDO
            if User.objects.filter(email=email).exists():
                messages.error(request, "El correo ingresado ya está registrado por otro usuario.")
                return redirect("gestionar_usuarios")

        if not usuario_id:
            password = request.POST.get("password")
            user = User.objects.create_user(username=username, email=email, password=password)
            PerfilUsuario.objects.create(user=user, rol=rol)
            Auditoria.objects.create(user=request.user, accion=f"Creó usuario {username}")
            messages.success(request, "Usuario creado correctamente.")
            return redirect("gestionar_usuarios")
        else:
            perfil_u = PerfilUsuario.objects.get(id=usuario_id)
            user = perfil_u.user
            user.username = username
            user.email = email
            user.save()
            perfil_u.rol = rol
            perfil_u.save()
            Auditoria.objects.create(user=request.user, accion=f"Editó usuario {username}")
            messages.success(request, "Usuario actualizado.")
            return redirect("gestionar_usuarios")

    return redirect("gestionar_usuarios")


@login_required
def eliminar_usuario_panel(request, perfil_id):
    perfil_admin = PerfilUsuario.objects.get(user=request.user)
    if perfil_admin.rol != "admin":
        return redirect("index")

    perfil_u = PerfilUsuario.objects.get(id=perfil_id)
    nombre = perfil_u.user.username
    user = perfil_u.user
    perfil_u.delete()
    user.delete()
    Auditoria.objects.create(user=request.user, accion=f"Eliminó usuario {nombre}")
    messages.success(request, "Usuario eliminado correctamente.")
    return redirect("gestionar_usuarios")


# ==========================================================
# AUDITORÍA AJAX
# ==========================================================
@login_required
def auditoria_fragment(request):
    auditorias = Auditoria.objects.select_related("user").order_by("-id")[:20]
    html = render_to_string("api/auditoria_fragment.html", {"auditorias": auditorias})
    return JsonResponse({"html": html})


# ==========================================================
# EXPORTACIÓN / IMPORTACIÓN
# ==========================================================
@login_required
def export_excel(request):
    calificaciones = list(Calificacion.objects.all().values(
        'empresa', 'periodo', 'tipo', 'calificacion', 'fuente', 'created_at'
    ))

    df = pd.DataFrame(calificaciones)

    if not df.empty:
        if 'created_at' in df.columns:
            df['created_at'] = df['created_at'].astype(str)

    
    from io import BytesIO
    output = BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Calificaciones')

    output.seek(0)

    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="calificaciones.xlsx"'

    return response


@login_required
def export_pdf(request):
    print("TOTAL REGISTROS:", Calificacion.objects.count())

    calificaciones = Calificacion.objects.all()
    html = render_to_string('api/pdf_template.html', {'calificaciones': calificaciones})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="calificaciones.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response


@login_required
def import_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        file = request.FILES['excel_file']
        df = pd.read_excel(file)

        for _, row in df.iterrows():
            Calificacion.objects.update_or_create(
                empresa=row['empresa'],
                periodo=row['periodo'],
                defaults={
                    'tipo': row.get('tipo', ''),
                    'calificacion': row.get('calificacion', ''),
                    'fuente': row.get('fuente', ''),
                }
            )
        messages.success(request, "Datos importados correctamente desde Excel.")
    return redirect("index")


# ==========================================================
# RECUPERAR CUENTA :D
# ========================================================== 
def recuperar_cuenta(request):
    if request.method == "POST":
        username = request.POST.get("username")

        try:
            user = User.objects.get(username=username)
            perfil = user.perfilusuario
        except User.DoesNotExist:
            return JsonResponse({"error": "El usuario no existe."}, status=400)

        # Reset de bloqueo
        perfil.intentos_fallidos = 0
        perfil.bloqueado_hasta = None
        perfil.save()

        return JsonResponse({"success": "Tu cuenta ha sido desbloqueada. Ya puedes iniciar sesión."})

    return render(request, "recuperar_cuenta.html")

from django.contrib.auth.decorators import user_passes_test

def es_admin(user):
    return user.is_superuser or user.perfilusuario.rol == "admin"



@user_passes_test(es_admin)
def admin_desbloquear_usuario(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")

        perfil = PerfilUsuario.objects.get(user_id=user_id)
        perfil.intentos_fallidos = 0
        perfil.bloqueado_hasta = None
        perfil.save()

        return JsonResponse({"success": "Usuario desbloqueado exitosamente."})

    # Mostrar usuarios bloqueados
    bloqueados = PerfilUsuario.objects.filter(bloqueado_hasta__isnull=False)

    return render(request, "admin_desbloqueo.html", {"bloqueados": bloqueados})

@user_passes_test(es_admin)
def admin_desbloqueo(request):
    bloqueados = PerfilUsuario.objects.filter(bloqueado_hasta__isnull=False)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        perfil = PerfilUsuario.objects.get(user_id=user_id)
        perfil.intentos_fallidos = 0
        perfil.bloqueado_hasta = None
        perfil.save()
        return redirect("admin_desbloqueo")

    return render(request, "api/admin_desbloqueo.html", {"bloqueados": bloqueados})
