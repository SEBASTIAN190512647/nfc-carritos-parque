from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Sum
from django.utils import timezone
from .models import Vehiculo, Mantenimiento, RegistroCaja, FondoJefe, Sugerencia
from .forms import MantenimientoForm

def cerrar_sesion(request):
    logout(request)
    return redirect('/')

@login_required 
def registrar_mantenimiento(request):
    vehiculo_id = request.GET.get('vehiculo_id')
    vehiculo_inicial = None
    
    if vehiculo_id:
        vehiculo_inicial = get_object_or_404(Vehiculo, id=vehiculo_id)

    if request.method == 'POST':
        form = MantenimientoForm(request.POST)
        if form.is_valid():
            mantenimiento = form.save(commit=False)
            mantenimiento.tecnico = request.user
            mantenimiento.save()
            return redirect('/admin/gestion/mantenimiento/')
    else:
        form = MantenimientoForm(initial={'vehiculo': vehiculo_inicial})

    return render(request, 'gestion/registrar_mantenimiento.html', {'form': form, 'vehiculo': vehiculo_inicial})

@login_required
def dashboard_caja(request):
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year

    registros = RegistroCaja.objects.filter(fecha__month=mes_actual, fecha__year=anio_actual).order_by('-fecha')
    total_caja = registros.aggregate(Sum('monto'))['monto__sum'] or 0

    return render(request, 'gestion/dashboard_caja.html', {
        'registros': registros,
        'total_caja': total_caja
    })

@login_required
def dashboard_general(request):
    fondos = FondoJefe.objects.all().order_by('-fecha')
    total_fondos = fondos.aggregate(Sum('monto'))['monto__sum'] or 0
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
def eliminar_fondo(request, pk):
    if request.user.groups.filter(name='Jefe').exists() or request.user.is_superuser:
        fondo = get_object_or_404(FondoJefe, pk=pk)
        fondo.delete()
    return redirect('dashboard_general')

@login_required
def eliminar_caja(request, pk):
    if request.user.groups.filter(name='Secretaria').exists() or request.user.is_superuser:
        registro = get_object_or_404(RegistroCaja, pk=pk)
        registro.delete()
    return redirect('dashboard_caja')

@login_required
def router_por_rol(request):
    """Enrutador maestro: redirige a la pantalla exacta según el usuario o grupo"""
    user = request.user
    
    if user.is_superuser or user.username == 'admin':
        return redirect('/admin/')
    elif user.username == 'jefe_parque' or user.groups.filter(name='Jefe').exists():
        return redirect('dashboard_general')
    elif user.username == 'secretaria_parque' or user.groups.filter(name='Secretaria').exists():
        return redirect('dashboard_caja')
    elif user.groups.filter(name='Tecnico').exists():
        return redirect('nuevo_mantenimiento')
    else:
        return redirect('nuevo_mantenimiento')