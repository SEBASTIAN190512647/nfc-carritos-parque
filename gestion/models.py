
from django.db import models
from django.contrib.auth.models import User

# 1. Modelo para los carritos
class Vehiculo(models.Model):
    ESTADOS = [
        ('Operativo', 'Operativo'),
        ('Mantenimiento', 'En Mantenimiento'),
        ('Fuera_Servicio', 'Fuera de Servicio')
    ]
    
    nombre = models.CharField(max_length=50)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Operativo')
    fecha_ingreso = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.nombre

# 2. Modelo para el Cuadre de Caja
class RegistroCaja(models.Model):
    fecha = models.DateField(auto_now_add=True)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    numero_recorridos = models.IntegerField(default=0)
    ingreso_bruto = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Caja {self.vehiculo.nombre} - {self.fecha}"

# 3. Modelo para el Mantenimiento Técnico
class Mantenimiento(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    
    voltaje_bateria = models.DecimalField(max_digits=4, decimal_places=2, help_text="Voltaje actual en V")
    descripcion_falla = models.TextField(help_text="¿Qué reparaste o mejoraste?")
    
    costo_repuestos = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    honorarios_tecnico = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    tecnico = models.ForeignKey(User, on_delete=models.CASCADE)

    def costo_total(self):
        return self.costo_repuestos + self.honorarios_tecnico

    def __str__(self):
        return f"Mantenimiento {self.vehiculo.nombre} - {self.fecha.strftime('%d/%m/%Y')}"
    
    # 4. Modelo para el Capital que envía el Jefe
class FondoJefe(models.Model):
    fecha = models.DateField(auto_now_add=True)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    descripcion = models.CharField(max_length=200, help_text="Ej: Envío para repuestos de Halloween")
    jefe = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Capital: ${self.monto} - {self.fecha}"

# 5. Modelo para la Caja de Sugerencias del Ingeniero (Tú)
class Sugerencia(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    titulo = models.CharField(max_length=100)
    idea = models.TextField(help_text="Propuesta innovadora para el parque")
    autor = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Idea: {self.titulo}"