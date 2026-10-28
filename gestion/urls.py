from django.urls import path
from . import views

urlpatterns = [
    path('mantenimiento/nuevo/', views.registrar_mantenimiento, name='nuevo_mantenimiento'),
    path('caja/dashboard/', views.dashboard_caja, name='dashboard_caja'),
    path('dashboard/', views.dashboard_general, name='dashboard_general'),
    path('sugerencia/nueva/', views.crear_sugerencia, name='crear_sugerencia'),
    path('fondo/nuevo/', views.crear_fondo, name='crear_fondo'),
    path('fondo/eliminar/<int:pk>/', views.eliminar_fondo, name='eliminar_fondo'),
    path('caja/eliminar/<int:pk>/', views.eliminar_caja, name='eliminar_caja'),
    path('dashboard/', views.router_por_rol, name='dashboard_general'),
    path('logout/', views.cerrar_sesion, name='logout'),
]

# urlpatterns = [
    
#     path('dashboard/', views.router_por_rol, name='router_por_rol'),
#     path('dashboard/jefe/', views.dashboard_general, name='dashboard_general'),
#     path('caja/dashboard/', views.dashboard_caja, name='dashboard_caja'),
#     path('mantenimiento/nuevo/', views.registrar_mantenimiento, name='nuevo_mantenimiento'),
#     path('fondo/nuevo/', views.crear_fondo, name='crear_fondo'),
#     path('sugerencia/nueva/', views.crear_sugerencia, name='crear_sugerencia'),
#     path('logout/', views.cerrar_sesion, name='logout'),
# ]
