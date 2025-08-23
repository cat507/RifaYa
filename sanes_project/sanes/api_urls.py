from django.urls import path
from . import views

urlpatterns = [
    # API de Rifas
    path('rifas/', views.api_rifa_list, name='api_rifa_list'),
    path('rifas/<int:pk>/', views.api_rifa_detail, name='api_rifa_detail'),
    path('rifas/<int:rifa_id>/comprar/', views.comprar_ticket_rifa, name='api_comprar_ticket'),
    
    # API de Sanes
    path('sanes/', views.api_san_list, name='api_san_list'),
    path('sanes/<int:pk>/', views.api_san_detail, name='api_san_detail'),
    
    # API de Usuarios
    path('usuarios/perfil/', views.user_profile, name='api_user_profile'),
]
