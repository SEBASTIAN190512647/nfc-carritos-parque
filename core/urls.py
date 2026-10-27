from django.contrib import admin
from django.urls import path, include

from django.shortcuts import redirect
urlpatterns = [
    path('', lambda request: redirect('/dashboard/')), # Si entran a la raíz, los manda al login o dashboard
    path('admin/', admin.site.urls),
    path('', include('gestion.urls')),
    
]
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/admin/login/'



    