from django import forms
from .models import Mantenimiento

class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = Mantenimiento
        # Seleccionamos qué campos quieres llenar desde tu celular
        fields = ['vehiculo', 'voltaje_bateria', 'descripcion_falla', 'costo_repuestos', 'honorarios_tecnico']
        widgets = {
            'descripcion_falla': forms.Textarea(attrs={'rows': 3}),
        }