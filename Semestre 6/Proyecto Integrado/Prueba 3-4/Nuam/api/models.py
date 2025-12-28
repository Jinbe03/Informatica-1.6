from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ============================
# ROLES DISPONIBLES
# ============================
ROLES = [
    ('corredor', 'Corredor'),
    ('admin', 'Administrador'),
    ('auditor', 'Auditor externo'),
]


# ============================
# PERFIL DE USUARIO + BLOQUEO
# ============================
class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROLES, default='corredor')

    # 🔒 BLOQUEO POR INTENTOS FALLIDOS
    intentos_fallidos = models.IntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.rol})"

    def esta_bloqueado(self):
        if self.bloqueado_hasta is None:
            return False
        return timezone.now() < self.bloqueado_hasta


# ============================
# CALIFICACIONES + FACTORES
# ============================
class Calificacion(models.Model):
    empresa = models.CharField(max_length=200)
    periodo = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)
    calificacion = models.CharField(max_length=50)
    fuente = models.CharField(max_length=200, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    # ========================
    # FACTORES PRINCIPALES (UI visibles)
    # ========================
    factor_08 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_09 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_10 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_11 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_20 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_37 = models.DecimalField(max_digits=16, decimal_places=6, default=0)

    # ========================
    # FACTORES AVANZADOS (ocultos en UI)
    # ========================
    factor_12 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_13 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_14 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_15 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_16 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_17 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_18 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_19 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_21 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_22 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_23 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_24 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_25 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_26 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_27 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_28 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_29 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_30 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_31 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_32 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_33 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_34 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_35 = models.DecimalField(max_digits=16, decimal_places=6, default=0)
    factor_36 = models.DecimalField(max_digits=16, decimal_places=6, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.empresa} - {self.periodo}"


# ============================
# AUDITORÍA (seguimiento)
# ============================
class Auditoria(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.accion}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Colores para consola
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        RED = "\033[91m"
        BLUE = "\033[94m"
        RESET = "\033[0m"

        accion_lower = self.accion.lower()

        if "exitoso" in accion_lower or "creó" in accion_lower:
            color = GREEN
        elif "intent" in accion_lower:
            color = YELLOW
        elif "bloqueada" in accion_lower or "elimin" in accion_lower:
            color = RED
        else:
            color = BLUE

        usuario = self.user.email if self.user else "Usuario desconocido"

        print(
            f"{color}[NUAM LOG] Usuario: {usuario} | Acción: {self.accion} | Fecha: {self.fecha}{RESET}"
        )
