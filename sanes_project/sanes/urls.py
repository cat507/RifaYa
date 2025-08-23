# sanes/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    # ---------------------
    # VISTAS PRINCIPALES
    # ---------------------
    path('', views.home, name='home'),
    
    # ---------------------
    # AUTENTICACIÓN
    # ---------------------
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # ---------------------
    # RIFAS
    # ---------------------
    path('rifas/', views.RifaListView.as_view(), name='rifa_list'),
    path('rifas/<int:pk>/', views.RifaDetailView.as_view(), name='rifa_detail'),
    path('rifas/crear/', views.RifaCreateView.as_view(), name='rifa_create'),
    path('rifas/<int:pk>/editar/', views.RifaUpdateView.as_view(), name='rifa_update'),
    path('rifas/<int:rifa_id>/comprar/', views.comprar_ticket_rifa, name='comprar_ticket_rifa'),
    path('rifas/<int:rifa_id>/checkout/', views.checkout_raffle, name='checkout_raffle'),
    
    # ---------------------
    # SANES
    # ---------------------
    path('sanes/', views.SanListView.as_view(), name='san_list'),
    path('sanes/<int:pk>/', views.SanDetailView.as_view(), name='san_detail'),
    path('sanes/crear/', views.SanCreateView.as_view(), name='san_create'),
    path('sanes/<int:pk>/editar/', views.SanUpdateView.as_view(), name='san_update'),
    path('sanes/<int:san_id>/inscribirse/', views.inscribirse_san, name='inscribirse_san'),
    path('sanes/<int:san_id>/checkout/', views.checkout_san, name='checkout_san'),
    
    # ---------------------
    # FACTURAS
    # ---------------------
    path('facturas/', views.FacturaListView.as_view(), name='factura_list'),
    path('facturas/<int:pk>/', views.FacturaDetailView.as_view(), name='factura_detail'),
    path('facturas/<int:factura_id>/subir-comprobante/', views.subir_comprobante_factura, name='subir_comprobante_factura'),
    
    # ---------------------
    # PAGOS
    # ---------------------
    path('pagos/cuota/<int:cupo_id>/', views.pagar_cuota_san, name='pagar_cuota_san'),
    
    # ---------------------
    # PERFIL DE USUARIO
    # ---------------------
    path('perfil/', views.user_profile, name='user_profile'),
    path('perfil/cambiar-foto/', views.cambiar_foto_perfil, name='cambiar_foto_perfil'),
    
    # ---------------------
    # ADMINISTRACIÓN
    # ---------------------
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/facturas/<int:factura_id>/confirmar/', views.confirmar_pago, name='confirmar_pago'),
    path('admin/facturas/<int:factura_id>/rechazar/', views.rechazar_pago, name='rechazar_pago'),
    
    # ---------------------
    # REPORTES
    # ---------------------
    path('reportes/rifas/', views.reporte_rifas, name='reporte_rifas'),
    path('reportes/sanes/', views.reporte_sanes, name='reporte_sanes'),
]