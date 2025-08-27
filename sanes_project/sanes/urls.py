from django.urls import path
from django.conf.urls import handler404, handler500
from . import views

urlpatterns = [
    # ---------------------
    # VISTAS DE AUTENTICACIÓN
    # ---------------------
    path('registro/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),

    # ---------------------
    # VISTAS PRINCIPALES
    # ---------------------
    path('', views.home, name='home'),

    # ---------------------
    # VISTAS DE PERFIL DE USUARIO
    # ---------------------
    path('perfil/', views.user_profile, name='user_profile'),
    path('perfil/editar/', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/cambiar-foto/', views.cambiar_foto_perfil, name='cambiar_foto_perfil'),
    path('notificaciones/', views.lista_notificaciones, name='lista_notificaciones'),

    # ---------------------
    # VISTAS DE RIFAS (CBV + FBV)
    # ---------------------
    path('rifas/', views.RifaListView.as_view(), name='rifa_list'),
    path('rifas/<int:pk>/', views.RifaDetailView.as_view(), name='rifa_detail'),
    path('rifas/crear/', views.RifaCreateView.as_view(), name='rifa_create'),
    path('rifas/<int:pk>/editar/', views.RifaUpdateView.as_view(), name='rifa_update'),
    path('rifas/<int:rifa_id>/comprar/', views.comprar_ticket_rifa, name='comprar_ticket_rifa'),
    path('rifas/<int:rifa_id>/checkout/', views.checkout_raffle, name='checkout_raffle'),
    path('rifas/historial/', views.historial_rifas, name='historial_rifas'),
    path('resultados-rifas/', views.resultados_rifas, name='resultados_rifas'),

    # Funciones FBV duplicadas de rifas
    path('rifas/lista/', views.lista_rifas, name='lista_rifas'),
    path('rifas/detalle/<int:rifa_id>/', views.detalle_rifa, name='detalle_rifa'),
    path('rifas/comprar/<int:rifa_id>/', views.comprar_ticket, name='comprar_ticket'),

    # ---------------------
    # VISTAS DE SANES (CBV + FBV)
    # ---------------------
    path('sanes/', views.SanListView.as_view(), name='san_list'),
    path('sanes/mis-sanes/', views.MisSanesView.as_view(), name='mis_sanes'),
    path('sanes/my-contributions/', views.MyContributionsView.as_view(), name='my_contributions'),
    path('sanes/<int:pk>/', views.SanDetailView.as_view(), name='san_detail'),
    path('sanes/crear/', views.SanCreateView.as_view(), name='san_create'),
    path('sanes/<int:pk>/editar/', views.SanUpdateView.as_view(), name='san_update'),
    path('sanes/<int:san_id>/inscribirse/', views.inscribirse_san, name='inscribirse_san'),
    path('sanes/<int:san_id>/checkout/', views.checkout_san, name='checkout_san'),
    path('sanes/historial/', views.historial_sanes, name='historial_sanes'),
    path('sanes/<int:san_id>/turnos/', views.turnos_san, name='turnos_san'),
    path('sanes/<int:san_id>/historial-pagos/', views.historial_pagos_san, name='historial_pagos_san'),
    path('sanes/participacion/<int:participacion_id>/adelantar-cuota/', views.adelantar_cuota_san, name='adelantar_cuota_san'),

    # Funciones FBV duplicadas de sanes
    path('sanes/lista/', views.lista_sanes, name='lista_sanes'),
    path('sanes/detalle/<int:san_id>/', views.detalle_san, name='detalle_san'),
    path('sanes/unirse/<int:san_id>/', views.unirse_san, name='unirse_san'),

    # ---------------------
    # VISTAS DE FACTURAS
    # ---------------------
    path('facturas/', views.FacturaListView.as_view(), name='factura_list'),
    path('facturas/<int:pk>/', views.FacturaDetailView.as_view(), name='factura_detail'),
    path('facturas/<int:factura_id>/pagar/', views.factura_pagar, name='factura_pagar'),
    path('facturas/<int:factura_id>/subir-comprobante/', views.subir_comprobante_factura, name='subir_comprobante_factura'),

    # ---------------------
    # VISTAS DE PAGOS
    # ---------------------
    path('cuotas/<int:cupo_id>/pagar/', views.pagar_cuota_san, name='pagar_cuota_san'),

    # ---------------------
    # VISTAS DE ADMINISTRACIÓN
    # ---------------------
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('dashboard/usuarios/<int:user_id>/', views.detalle_usuario, name='detalle_usuario'),
    path('dashboard/rifas/crear/', views.crear_rifa, name='crear_rifa'),
    path('dashboard/rifas/<int:rifa_id>/finalizar/', views.finalizar_rifa, name='finalizar_rifa'),
    path('dashboard/sanes/crear/', views.crear_san, name='crear_san'),
    path('dashboard/notificaciones/enviar/', views.enviar_notificacion_global, name='enviar_notificacion_global'),
    path('dashboard/reportes/finanzas/', views.reporte_finanzas, name='reporte_finanzas'),
    path('dashboard/sanes/<int:san_id>/asignar-turnos/', views.asignar_turnos_san, name='asignar_turnos_san'),
    path('dashboard/pagos/<int:factura_id>/confirmar/', views.confirmar_pago, name='confirmar_pago'),
    path('dashboard/pagos/<int:factura_id>/rechazar/', views.rechazar_pago, name='rechazar_pago'),
    path('dashboard/reportes/rifas/pdf/', views.exportar_reporte_rifas_pdf, name='exportar_reporte_rifas_pdf'),
    
    # URLs adicionales para admin views
    path('dashboard/users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('dashboard/users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('dashboard/rifas/', views.AdminRifaListView.as_view(), name='admin_rifa_list'),
    path('dashboard/sanes/', views.AdminSanListView.as_view(), name='admin_san_list'),
    path('dashboard/facturas/', views.AdminFacturaListView.as_view(), name='admin_factura_list'),
    path('dashboard/reportes/', views.AdminReporteView.as_view(), name='admin_reportes'),
    
    # URLs para gestión de facturas (admin)
    path('dashboard/facturas/<int:factura_id>/cambiar-estado/', views.cambiar_estado_factura, name='cambiar_estado_factura'),
    
    # URLs para logs del sistema
    path('dashboard/logs/', views.admin_logs, name='admin_logs'),
    path('dashboard/logs/exportar/', views.exportar_logs, name='exportar_logs'),

    # ---------------------
    # VISTAS DE COMENTARIOS
    # ---------------------
    path('comentarios/agregar/<int:content_type_id>/<int:object_id>/', views.agregar_comentario, name='agregar_comentario'),
    path('comentarios/eliminar/<int:comentario_id>/', views.eliminar_comentario, name='eliminar_comentario'),

    # ---------------------
    # VISTAS DE NOTIFICACIONES
    # ---------------------
    path('notificaciones/', views.notificaciones_usuario, name='notificaciones_usuario'),
    path('notificaciones/marcar-leida/<int:notificacion_id>/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('notificaciones/marcar-todas-leidas/', views.marcar_todas_leidas, name='marcar_todas_leidas'),
    path('notificaciones/ajax/', views.obtener_notificaciones_ajax, name='obtener_notificaciones_ajax'),

    # ---------------------
    # VISTAS DE REPORTES
    # ---------------------
    path('reportes/rifas/', views.reporte_rifas, name='reporte_rifas'),
    path('reportes/sanes/', views.reporte_sanes, name='reporte_sanes'),

    # ---------------------
    # API REST
    # ---------------------
    path('api/rifas/', views.api_rifa_list, name='api_rifa_list'),
    path('api/rifas/<int:pk>/', views.api_rifa_detail, name='api_rifa_detail'),
    path('api/sanes/', views.api_san_list, name='api_san_list'),
    path('api/sanes/<int:pk>/', views.api_san_detail, name='api_san_detail'),
]

# ---------------------
# MANEJO DE ERRORES
# ---------------------
handler404 = views.handler404
handler500 = views.handler500
