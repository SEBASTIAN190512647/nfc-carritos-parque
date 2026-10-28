from django.shortcuts import render
from .models import Vehiculo, Mantenimiento, RegistroCaja, FondoJefe, Sugerencia
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import MantenimientoForm
from django.contrib.auth import logout

def cerrar_sesion(request):
    logout(request)
    return redirect('/')

@login_required # Esto asegura que solo tú (o alguien logueado) pueda registrar mantenimientos
def registrar_mantenimiento(request):
    # Intentamos obtener el ID del vehículo desde la URL (lo enviará el NFC)
    vehiculo_id = request.GET.get('vehiculo_id')
    vehiculo_inicial = None
    
    if vehiculo_id:
        vehiculo_inicial = get_object_or_404(Vehiculo, id=vehiculo_id)

    if request.method == 'POST':
        form = MantenimientoForm(request.POST)
        if form.is_valid():
            mantenimiento = form.save(commit=False)
            mantenimiento.tecnico = request.user # Asigna automáticamente tu usuario
            mantenimiento.save()
            return redirect('/admin/gestion/mantenimiento/') # Te redirige al historial al terminar
    else:
        # Si vienes del NFC, pre-seleccionamos el vehículo
        form = MantenimientoForm(initial={'vehiculo': vehiculo_inicial})

    return render(request, 'gestion/registrar_mantenimiento.html', {'form': form, 'vehiculo': vehiculo_inicial})

from django.db.models import Sum
from django.utils import timezone
# Asegúrate de que RegistroCaja esté importado junto a Vehiculo y Mantenimiento

@login_required
def dashboard_caja(request):
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year

    # Filtramos solo los mantenimientos de este mes
    mantenimientos = Mantenimiento.objects.filter(fecha__month=mes_actual, fecha__year=anio_actual)
    
    # Sumamos automáticamente los costos
    total_repuestos = mantenimientos.aggregate(Sum('costo_repuestos'))['costo_repuestos__sum'] or 0
    total_honorarios = mantenimientos.aggregate(Sum('honorarios_tecnico'))['honorarios_tecnico__sum'] or 0
    total_gastos = total_repuestos + total_honorarios

    return render(request, 'gestion/dashboard.html', {
        'total_repuestos': total_repuestos,
        'total_honorarios': total_honorarios,
        'total_gastos': total_gastos,
        'mantenimientos': mantenimientos
    })
    


@login_required
def dashboard_general(request):
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year
    
    # Sumamos los fondos inyectados por el jefe este mes
    fondos_mes = FondoJefe.objects.filter(fecha__month=mes_actual, fecha__year=anio_actual)
    total_fondos = fondos_mes.aggregate(Sum('monto'))['monto__sum'] or 0
    
    # fondos visualizados
    fondos = FondoJefe.objects.all().order_by('-fecha')
    total_fondos = fondos.aggregate(Sum('monto'))['monto__sum'] or 0
    
    # Obtenemos las sugerencias técnicas ordenadas de la más reciente a la más antigua
    sugerencias = Sugerencia.objects.all().order_by('-fecha')
    
    
    return render(request, 'gestion/dashboard_general.html', {
        'total_fondos': total_fondos,
        'fondos': fondos,
        'sugerencias': sugerencias,
    })

@login_required
def crear_sugerencia(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        idea = request.POST.get('idea')
        if titulo and idea:
            Sugerencia.objects.create(titulo=titulo, idea=idea, autor=request.user)
    return redirect('dashboard_general')

@login_required
def crear_fondo(request):
    if request.method == 'POST':
        monto = request.POST.get('monto')
        descripcion = request.POST.get('descripcion')
        if monto and descripcion:
            FondoJefe.objects.create(monto=monto, descripcion=descripcion, jefe=request.user)
    return redirect('dashboard_general')

@login_required
def router_por_rol(request):
    """Enrutador maestro: redirige seguro según el usuario"""
    user = request.user
    
    if user.is_superuser or user.username == 'admin':
        return redirect('/admin/')
    elif user.username == 'jefe_parque' or user.groups.filter(name='Jefe').exists():
        return redirect('dashboard_general')
    elif user.username == 'secretaria_parque' or user.groups.filter(name='Secretaria').exists():
        return redirect('dashboard_caja')
    else:
        # Para el técnico u otros usuarios
        return redirect('nuevo_mantenimiento') 


    
   