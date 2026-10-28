from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from django.http import HttpResponseForbidden
from .models import Vehiculo, Mantenimiento, RegistroCaja, FondoJefe, Sugerencia
from .forms import MantenimientoForm, RegistroCajaForm


def usuario_tiene_rol(user, *roles):
    nombres = {nombre.casefold() for nombre in user.groups.values_list('name', flat=True)}
    nombres.add(user.username.casefold())
    return user.is_superuser or bool(nombres.intersection({rol.casefold() for rol in roles}))


def rol_actual(user):
    if user.is_superuser or usuario_tiene_rol(user, 'admin'):
        return 'Administrador'
    if usuario_tiene_rol(user, 'jefe', 'jefe_parque'):
        return 'Jefe'
    if usuario_tiene_rol(user, 'secretaria', 'secretaria_parque'):
        return 'Secretaria'
    if usuario_tiene_rol(user, 'tecnico', 'tecnico_parque'):
        return 'Tecnico'
    return 'Tecnico'


def exigir_rol(request, *roles):
    if rol_actual(request.user) not in roles and not request.user.is_superuser:
        return HttpResponseForbidden('No tienes permisos para acceder a este panel.')
    return None

def cerrar_sesion(request):
    logout(request)
    return redirect('/')

@login_required 
def registrar_mantenimiento(request):
    acceso = exigir_rol(request, 'Tecnico')
    if acceso:
        return acceso
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
            return redirect('dashboard_tecnico')
    else:
        form = MantenimientoForm(initial={'vehiculo': vehiculo_inicial})

    return render(request, 'gestion/registrar_mantenimiento.html', {'form': form, 'vehiculo': vehiculo_inicial})

@login_required
def dashboard_caja(request):
    acceso = exigir_rol(request, 'Secretaria')
    if acceso:
        return acceso
    mes_actual = timezone.now().month
    anio_actual = timezone.now().year

    registros = RegistroCaja.objects.filter(fecha__month=mes_actual, fecha__year=anio_actual).order_by('-fecha')
    total_caja = registros.aggregate(Sum('ingreso_bruto'))['ingreso_bruto__sum'] or 0
    form = RegistroCajaForm()

    return render(request, 'gestion/dashboard_caja.html', {
        'registros': registros,
        'total_caja': total_caja,
        'form': form,
    })


@login_required
def registrar_caja(request):
    acceso = exigir_rol(request, 'Secretaria')
    if acceso:
        return acceso
    if request.method != 'POST':
        return redirect('dashboard_caja')
    form = RegistroCajaForm(request.POST)
    if form.is_valid():
        registro = form.save(commit=False)
        registro.registrado_por = request.user
        registro.save()
    return redirect('dashboard_caja')

@login_required
def dashboard_general(request):
    acceso = exigir_rol(request, 'Jefe')
    if acceso:
        return acceso
    fondos = FondoJefe.objects.all().order_by('-fecha')
    total_fondos = fondos.aggregate(Sum('monto'))['monto__sum'] or 0
    total_ingresos = RegistroCaja.objects.aggregate(Sum('ingreso_bruto'))['ingreso_bruto__sum'] or 0
    sugerencias = Sugerencia.objects.all().order_by('-fecha')
    mantenimientos = Mantenimiento.objects.select_related('vehiculo', 'tecnico').order_by('-fecha')[:8]
    costo = ExpressionWrapper(F('costo_repuestos') + F('honorarios_tecnico'), output_field=DecimalField(max_digits=10, decimal_places=2))
    total_mantenimiento = Mantenimiento.objects.aggregate(total=Sum(costo))['total'] or 0

    return render(request, 'gestion/dashboard_general.html', {
        'total_fondos': total_fondos,
        'total_ingresos': total_ingresos,
        'fondos': fondos,
        'sugerencias': sugerencias,
        'mantenimientos': mantenimientos,
        'total_mantenimiento': total_mantenimiento,
        'vehiculos': Vehiculo.objects.all().order_by('nombre'),
    })


@login_required
def dashboard_tecnico(request):
    acceso = exigir_rol(request, 'Tecnico')
    if acceso:
        return acceso
    return render(request, 'gestion/dashboard_tecnico.html', {
        'form': MantenimientoForm(),
        'vehiculos': Vehiculo.objects.all().order_by('nombre'),
        'mantenimientos': Mantenimiento.objects.filter(tecnico=request.user).select_related('vehiculo').order_by('-fecha')[:10],
    })

@login_required
def crear_sugerencia(request):
    acceso = exigir_rol(request, 'Jefe', 'Tecnico')
    if acceso:
        return acceso
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        idea = request.POST.get('idea')
        if titulo and idea:
            Sugerencia.objects.create(titulo=titulo, idea=idea, autor=request.user)
    return redirect('dashboard_general')

@login_required
def crear_fondo(request):
    acceso = exigir_rol(request, 'Jefe')
    if acceso:
        return acceso
    if request.method == 'POST':
        monto = request.POST.get('monto')
        descripcion = request.POST.get('descripcion')
        if monto and descripcion:
            FondoJefe.objects.create(monto=monto, descripcion=descripcion, jefe=request.user)
    return redirect('dashboard_general')

@login_required
def eliminar_fondo(request, pk):
    if request.method == 'POST' and usuario_tiene_rol(request.user, 'Jefe', 'jefe_parque'):
        fondo = get_object_or_404(FondoJefe, pk=pk)
        fondo.delete()
    return redirect('dashboard_general')

@login_required
def eliminar_caja(request, pk):
    if request.method == 'POST' and usuario_tiene_rol(request.user, 'Secretaria', 'secretaria_parque'):
        registro = get_object_or_404(RegistroCaja, pk=pk)
        registro.delete()
    return redirect('dashboard_caja')

@login_required
def router_por_rol(request):
    """Enrutador maestro: redirige a la pantalla exacta según el usuario o grupo"""
    user = request.user
    
    if user.is_superuser or user.username.casefold() == 'admin':
        return redirect('/admin/')
    elif rol_actual(user) == 'Jefe':
        return redirect('dashboard_general')
    elif rol_actual(user) == 'Secretaria':
        return redirect('dashboard_caja')
    else:
        return redirect('dashboard_tecnico')