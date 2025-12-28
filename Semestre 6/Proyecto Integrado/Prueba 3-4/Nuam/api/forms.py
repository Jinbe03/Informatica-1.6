from django import forms
from .models import Calificacion

# =====================================
# FORMULARIO PRINCIPAL (CRUD CALIFICACIONES)
# =====================================
class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = [
            "empresa",
            "periodo",
            "tipo",
            "calificacion",
            "fuente",
            "observaciones",

            # 👉 Factores principales que vamos a manejar en UI
            "factor_08",
            "factor_09",
            "factor_10",
            "factor_11",
            "factor_20",
            "factor_37",
        ]
        widgets = {
            "empresa": forms.TextInput(attrs={"class": "form-control"}),
            "periodo": forms.TextInput(attrs={"type": "month", "class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "calificacion": forms.TextInput(attrs={"class": "form-control"}),
            "fuente": forms.TextInput(attrs={"class": "form-control"}),
            "observaciones": forms.Textarea(attrs={"class": "form-control", "rows": 2}),

            # =============================
            # Widgets para factores PRINCIPALES
            # =============================
            "factor_08": forms.NumberInput(attrs={"class": "form-control", "step": "0.000001"}),
            "factor_09": forms.NumberInput(attrs={"class": "form-control", "step": "0.000001"}),
            "factor_10": forms.NumberInput(attrs={"class": "form-control", "step": "0.000001"}),
            "factor_11": forms.NumberInput(attrs={"class": "form-control", "step": "0.000001"}),
            "factor_20": forms.NumberInput(attrs={"class": "form-control", "step": "0.000001"}),
            "factor_37": forms.NumberInput(attrs={"class": "form-control", "step": "0.000001"}),
        }


# =====================================
# FORMULARIO PARA FILTROS
# =====================================

TIPOS_CHOICES = [
    ('IVA-Renta', 'IVA-Renta'),
    ('IVA', 'IVA'),
    ('Renta', 'Renta'),
]

class FiltroCalificacionForm(forms.Form):
    empresa = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre de empresa',
            'class': 'form-control'
        })
    )

    tipo = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + TIPOS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
