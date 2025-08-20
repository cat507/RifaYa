# sanes_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rutas de la app principal
    path('', include('sanes.urls')),  # las URLs principales ya están ahí

    # Rutas de autenticación de allauth
    path('accounts/', include('allauth.urls')),

    # API (si crece, se puede mover a otro archivo más adelante)
    path('api/', include('sanes.api_urls')),
]

# Servir archivos estáticos/media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
