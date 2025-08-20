from django.urls import path
from . import views  # Importamos las vistas de la app

urlpatterns = [
    path("", views.api_home, name="api_home"),  # Ruta base de la API
]
