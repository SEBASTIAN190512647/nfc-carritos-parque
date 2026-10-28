from django import forms
from .models import Mantenimiento, RegistroCaja

class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = Mantenimiento
        # Seleccionamos qué campos quieres llenar desde tu celular
        fields = ['vehiculo', 'voltaje_bateria', 'descripcion_falla', 'costo_repuestos', 'honorarios_tecnico']
        widgets = {
            'descripcion_falla': forms.Textarea(attrs={'rows': 3}),
        }


class RegistroCajaForm(forms.ModelForm):
    class Meta:
        model = RegistroCaja
        fields = ['vehiculo', 'numero_recorridos', 'ingreso_bruto']
        widgets = {
            'numero_recorridos': forms.NumberInput(attrs={'min': 0}),
            'ingreso_bruto': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
        }