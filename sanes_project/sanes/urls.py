# sanes/urls.py
from django.urls import path, include
from . import views

# Vistas API
from .views import SanListAPIView, CupoListAPIView

urlpatterns = [
    # --- Vistas Principales ---
    path('', views.home, name='home'),
    path('sanes-y-rifas/', views.san_list, name='san_list'),
    path('raffle/<int:raffle_id>/', views.raffle_detail, name='raffle_detail'),
    path('create-raffle/', views.create_raffle, name='create_raffle'),
    path('buy-raffle-tickets/<int:raffle_id>/', views.buy_raffle_tickets, name='buy_raffle_tickets'),

    # --- Autenticación y Perfil ---
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.user_profile_view, name='user_profile'),
    path('perfil/cambiar-foto/', views.cambiar_foto_perfil, name='cambiar_foto_perfil'),


    # --- SANes ---
    path('mis-sanes/', views.mis_sanes, name='mis_sanes'),
    path('san/<int:san_id>/', views.san_detail, name='san_detail'), # Corregido
    path('buy-san/<int:san_id>/', views.buy_san, name='buy_san'),
    path('confirmar-compra/<int:san_id>/', views.confirmar_compra, name='confirm_purchase'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('create-san/', views.create_san, name='create_san'),
    path('mis-contribuciones/', views.my_contributions_view, name='my_contributions'),
    path('san/<int:san_id>/generar-ticket/', views.generar_ticket_san, name='generar_ticket_san'),

    # --- APIs ---
    path('api/sanes/', SanListAPIView.as_view(), name='san_list_api'),
    path('api/cupos/', CupoListAPIView.as_view(), name='cupo_list_api'),
    path("", views.api_home, name="api_home"),
]