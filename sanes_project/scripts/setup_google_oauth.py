#!/usr/bin/env python
"""
Script para configurar Google OAuth en django-allauth
Ejecutar: python manage.py shell < scripts/setup_google_oauth.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sanes_project.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider

def setup_google_oauth():
    """Configurar Google OAuth en django-allauth"""
    
    # Obtener o crear el sitio
    site, created = Site.objects.get_or_create(
        id=1,
        defaults={
            'domain': 'localhost:8000',
            'name': 'Rifas Anica'
        }
    )
    
    if created:
        print(f"✅ Sitio creado: {site.name} ({site.domain})")
    else:
        print(f"✅ Sitio existente: {site.name} ({site.domain})")
    
    # Verificar si ya existe la app de Google
    try:
        google_app = SocialApp.objects.get(provider='google')
        print(f"✅ App de Google ya existe: {google_app.name}")
        
        # Actualizar con las nuevas credenciales si están disponibles
        client_id = os.environ.get('GOOGLE_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        
        if client_id and client_secret:
            google_app.client_id = client_id
            google_app.secret = client_secret
            google_app.save()
            print("✅ Credenciales de Google actualizadas")
        
    except SocialApp.DoesNotExist:
        # Crear la app de Google
        client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
        client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
        
        if not client_id or not client_secret:
            print("⚠️  ADVERTENCIA: No se encontraron las credenciales de Google")
            print("   Configura las variables de entorno:")
            print("   - GOOGLE_CLIENT_ID")
            print("   - GOOGLE_CLIENT_SECRET")
            print("   O configura manualmente en el admin de Django")
            return
        
        google_app = SocialApp.objects.create(
            provider='google',
            name='Google',
            client_id=client_id,
            secret=client_secret
        )
        
        # Asociar con el sitio
        google_app.sites.add(site)
        
        print(f"✅ App de Google creada: {google_app.name}")
        print(f"   Client ID: {client_id[:20]}...")
    
    print("\n🎉 Configuración de Google OAuth completada!")
    print("\n📝 Próximos pasos:")
    print("1. Ve al admin de Django: http://localhost:8000/admin/")
    print("2. Verifica que la app de Google esté configurada correctamente")
    print("3. Prueba el login con Google en: http://localhost:8000/accounts/login/")

if __name__ == '__main__':
    setup_google_oauth()

