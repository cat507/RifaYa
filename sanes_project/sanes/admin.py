# sanes/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    CustomUser, Factura, Rifa, Ticket, San, ParticipacionSan, 
    Cupo, Comment, SystemLog, PagoSimulado, NotificacionMejorada,
    Notificacion, Reporte, HistorialAccion, SorteoRifa, TurnoSan, Mensaje
)

# ---------------------
# ADMINISTRACIÓN DE USUARIOS
# ---------------------
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'rol', 'is_active', 'date_joined')
    list_filter = ('rol', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'cedula')
    readonly_fields = ('date_joined', 'last_login')
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('username', 'email', 'first_name', 'last_name', 'foto_perfil')
        }),
        ('Información de Contacto', {
            'fields': ('phone_number', 'address')
        }),
        ('Información Adicional', {
            'fields': ('date_of_birth', 'cedula', 'oficio')
        }),
        ('Permisos y Estado', {
            'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activar_usuarios', 'desactivar_usuarios', 'hacer_administradores', 'hacer_usuarios']
    
    @admin.action(description='Activar usuarios seleccionados')
    def activar_usuarios(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} usuarios han sido activados.")
    
    @admin.action(description='Desactivar usuarios seleccionados')
    def desactivar_usuarios(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} usuarios han sido desactivados.")
    
    @admin.action(description='Hacer administradores')
    def hacer_administradores(self, request, queryset):
        queryset.update(rol='administrador')
        self.message_user(request, f"{queryset.count()} usuarios ahora son administradores.")
    
    @admin.action(description='Hacer usuarios regulares')
    def hacer_usuarios(self, request, queryset):
        queryset.update(rol='usuario')
        self.message_user(request, f"{queryset.count()} usuarios ahora son usuarios regulares.")


# ---------------------
# ADMINISTRACIÓN DE FACTURAS
# ---------------------
@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'usuario', 'get_tipo_contenido', 'monto_total', 'monto_pagado', 'estado_pago', 'fecha_emision', 'fecha_vencimiento')
    list_filter = ('estado_pago', 'metodo_pago', 'fecha_emision', 'fecha_vencimiento')
    search_fields = ('codigo', 'usuario__email', 'usuario__username')
    readonly_fields = ('codigo', 'fecha_emision')
    
    def get_tipo_contenido(self, obj):
        """Retorna el tipo de contenido de la factura"""
        return obj.get_tipo_contenido()
    get_tipo_contenido.short_description = 'Tipo de Contenido'
    
    fieldsets = (
        ('Información de la Factura', {
            'fields': ('codigo', 'usuario', 'content_type', 'object_id')
        }),
        ('Información Financiera', {
            'fields': ('monto_total', 'monto_pagado', 'estado_pago', 'metodo_pago')
        }),
        ('Fechas', {
            'fields': ('fecha_emision', 'fecha_vencimiento')
        }),
        ('Documentos', {
            'fields': ('comprobante_pago', 'notas')
        }),
    )
    
    actions = ['confirmar_pagos', 'rechazar_pagos', 'marcar_vencidas']
    
    @admin.action(description='Confirmar pagos seleccionados')
    def confirmar_pagos(self, request, queryset):
        for factura in queryset:
            factura.confirmar_pago()
        self.message_user(request, f"{queryset.count()} facturas han sido confirmadas.")
    
    @admin.action(description='Rechazar pagos seleccionados')
    def rechazar_pagos(self, request, queryset):
        for factura in queryset:
            factura.rechazar_pago()
        self.message_user(request, f"{queryset.count()} facturas han sido rechazadas.")
    
    @admin.action(description='Marcar como vencidas')
    def marcar_vencidas(self, request, queryset):
        for factura in queryset:
            if factura.is_vencida():
                factura.estado_pago = 'vencida'
                factura.save()
        self.message_user(request, f"{queryset.count()} facturas han sido marcadas como vencidas.")


# ---------------------
# ADMINISTRACIÓN DE RIFAS
# ---------------------
@admin.register(Rifa)
class RifaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'organizador', 'estado', 'precio_ticket', 'tickets_vendidos', 'porcentaje_vendido', 'fecha_inicio', 'fecha_fin')
    list_filter = ('estado', 'fecha_inicio', 'fecha_fin')
    search_fields = ('titulo', 'organizador__username', 'organizador__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'premio', 'imagen')
        }),
        ('Configuración', {
            'fields': ('precio_ticket', 'total_tickets', 'tickets_disponibles')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Organización', {
            'fields': ('organizador', 'estado', 'ganador')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activar_rifas', 'pausar_rifas', 'finalizar_rifas', 'seleccionar_ganadores']
    
    @admin.action(description='Activar rifas seleccionadas')
    def activar_rifas(self, request, queryset):
        queryset.update(estado='activa')
        self.message_user(request, f"{queryset.count()} rifas han sido activadas.")
    
    @admin.action(description='Pausar rifas seleccionadas')
    def pausar_rifas(self, request, queryset):
        queryset.update(estado='pausada')
        self.message_user(request, f"{queryset.count()} rifas han sido pausadas.")
    
    @admin.action(description='Finalizar rifas seleccionadas')
    def finalizar_rifas(self, request, queryset):
        queryset.update(estado='finalizada')
        self.message_user(request, f"{queryset.count()} rifas han sido finalizadas.")
    
    @admin.action(description='Seleccionar ganadores')
    def seleccionar_ganadores(self, request, queryset):
        for rifa in queryset:
            if rifa.estado == 'activa':
                rifa.seleccionar_ganador()
        self.message_user(request, f"Se han seleccionado ganadores para {queryset.count()} rifas.")


# ---------------------
# ADMINISTRACIÓN DE TICKETS
# ---------------------
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'numero', 'rifa', 'usuario', 'precio_pagado', 'fecha_compra', 'activo')
    list_filter = ('activo', 'fecha_compra', 'rifa__estado')
    search_fields = ('codigo', 'rifa__titulo', 'usuario__username', 'usuario__email')
    readonly_fields = ('codigo', 'fecha_compra')
    
    fieldsets = (
        ('Información del Ticket', {
            'fields': ('codigo', 'numero', 'rifa', 'usuario')
        }),
        ('Información de Compra', {
            'fields': ('precio_pagado', 'fecha_compra', 'factura')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
    )


# ---------------------
# ADMINISTRACIÓN DE SANES
# ---------------------
@admin.register(San)
class SanAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'organizador', 'estado', 'precio_total', 'numero_cuotas', 'participantes_actuales', 'cupos_disponibles', 'fecha_inicio', 'fecha_fin')
    list_filter = ('estado', 'tipo', 'frecuencia_pago', 'fecha_inicio', 'fecha_fin')
    search_fields = ('nombre', 'organizador__username', 'organizador__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'imagen')
        }),
        ('Configuración Financiera', {
            'fields': ('precio_total', 'numero_cuotas', 'precio_cuota')
        }),
        ('Configuración de Participantes', {
            'fields': ('total_participantes', 'participantes_actuales')
        }),
        ('Configuración de Pagos', {
            'fields': ('frecuencia_pago', 'tipo', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Organización', {
            'fields': ('organizador',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activar_sanes', 'pausar_sanes', 'finalizar_sanes']
    
    @admin.action(description='Activar sanes seleccionados')
    def activar_sanes(self, request, queryset):
        queryset.update(estado='activo')
        self.message_user(request, f"{queryset.count()} sanes han sido activados.")
    
    @admin.action(description='Pausar sanes seleccionados')
    def pausar_sanes(self, request, queryset):
        queryset.update(estado='pausado')
        self.message_user(request, f"{queryset.count()} sanes han sido pausados.")
    
    @admin.action(description='Finalizar sanes seleccionados')
    def finalizar_sanes(self, request, queryset):
        queryset.update(estado='finalizado')
        self.message_user(request, f"{queryset.count()} sanes han sido finalizados.")


# ---------------------
# ADMINISTRACIÓN DE PARTICIPACIONES EN SAN
# ---------------------
@admin.register(ParticipacionSan)
class ParticipacionSanAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'san', 'orden_cobro', 'cuotas_pagadas', 'cuotas_pendientes', 'porcentaje_completado', 'activa', 'fecha_inscripcion')
    list_filter = ('activa', 'san__estado', 'fecha_inscripcion')
    search_fields = ('usuario__username', 'usuario__email', 'san__nombre')
    readonly_fields = ('fecha_inscripcion',)
    
    fieldsets = (
        ('Participación', {
            'fields': ('usuario', 'san', 'orden_cobro', 'activa')
        }),
        ('Seguimiento de Cuotas', {
            'fields': ('cuotas_pagadas', 'fecha_ultima_cuota')
        }),
        ('Fechas', {
            'fields': ('fecha_inscripcion',),
            'classes': ('collapse',)
        }),
    )


# ---------------------
# ADMINISTRACIÓN DE CUPOS
# ---------------------
@admin.register(Cupo)
class CupoAdmin(admin.ModelAdmin):
    list_display = ('numero_semana', 'san', 'participacion', 'estado', 'asignado', 'monto_cuota', 'fecha_vencimiento', 'fecha_pago')
    list_filter = ('estado', 'asignado', 'san__estado')
    search_fields = ('san__nombre', 'participacion__usuario__username')
    readonly_fields = ('numero_semana',)
    
    fieldsets = (
        ('Información del Cupo', {
            'fields': ('numero_semana', 'san', 'estado', 'asignado')
        }),
        ('Asignación', {
            'fields': ('participacion', 'fecha_vencimiento')
        }),
        ('Pago', {
            'fields': ('monto_cuota', 'fecha_pago', 'factura')
        }),
    )


# ---------------------
# ADMINISTRACIÓN DE COMENTARIOS
# ---------------------
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'get_contenido', 'get_short_text', 'fecha_creacion', 'activo')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('usuario__username', 'texto')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    
    def get_contenido(self, obj):
        """Retorna el contenido al que pertenece el comentario"""
        if obj.content_object:
            return f"{obj.content_type.model}: {obj.content_object}"
        return "Sin contenido"
    get_contenido.short_description = 'Contenido'
    
    def get_short_text(self, obj):
        """Retorna el texto truncado del comentario"""
        return obj.get_short_text()
    get_short_text.short_description = 'Comentario'
    
    fieldsets = (
        ('Comentario', {
            'fields': ('usuario', 'texto', 'activo')
        }),
        ('Contenido', {
            'fields': ('content_type', 'object_id')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activar_comentarios', 'desactivar_comentarios']
    
    @admin.action(description='Activar comentarios seleccionados')
    def activar_comentarios(self, request, queryset):
        queryset.update(activo=True)
        self.message_user(request, f"{queryset.count()} comentarios han sido activados.")
    
    @admin.action(description='Desactivar comentarios seleccionados')
    def desactivar_comentarios(self, request, queryset):
        queryset.update(activo=False)
        self.message_user(request, f"{queryset.count()} comentarios han sido desactivados.")


# ---------------------
# ADMINISTRACIÓN DE LOGS DEL SISTEMA
# ---------------------
@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('tipo_accion', 'usuario', 'nivel', 'descripcion', 'fecha_creacion')
    list_filter = ('tipo_accion', 'nivel', 'fecha_creacion')
    search_fields = ('usuario__username', 'descripcion')
    readonly_fields = ('fecha_creacion', 'ip_address', 'user_agent')
    
    fieldsets = (
        ('Información de la Acción', {
            'fields': ('tipo_accion', 'nivel', 'descripcion')
        }),
        ('Usuario y Objeto', {
            'fields': ('usuario', 'content_type', 'object_id')
        }),
        ('Información Técnica', {
            'fields': ('ip_address', 'user_agent', 'datos_adicionales'),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )


# ---------------------
# ADMINISTRACIÓN DE PAGOS SIMULADOS
# ---------------------
@admin.register(PagoSimulado)
class PagoSimuladoAdmin(admin.ModelAdmin):
    list_display = ('codigo_transaccion', 'usuario', 'factura', 'metodo_pago', 'monto', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'metodo_pago', 'fecha_creacion')
    search_fields = ('codigo_transaccion', 'usuario__username', 'factura__codigo')
    readonly_fields = ('codigo_transaccion', 'fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información de la Transacción', {
            'fields': ('codigo_transaccion', 'usuario', 'factura')
        }),
        ('Información del Pago', {
            'fields': ('metodo_pago', 'monto', 'moneda', 'estado')
        }),
        ('Detalles de la Simulación', {
            'fields': ('referencia_externa', 'fecha_procesamiento', 'tiempo_procesamiento', 'intentos')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['procesar_pagos', 'reintentar_pagos']
    
    @admin.action(description='Procesar pagos seleccionados')
    def procesar_pagos(self, request, queryset):
        for pago in queryset:
            if pago.estado == 'pendiente':
                pago.procesar_pago()
        self.message_user(request, f"Se han procesado {queryset.count()} pagos.")
    
    @admin.action(description='Reintentar pagos fallidos')
    def reintentar_pagos(self, request, queryset):
        for pago in queryset:
            if pago.estado in ['fallido', 'cancelado']:
                pago.reintentar()
        self.message_user(request, f"Se han reintentado {queryset.count()} pagos.")


# ---------------------
# ADMINISTRACIÓN DE NOTIFICACIONES MEJORADAS
# ---------------------
@admin.register(NotificacionMejorada)
class NotificacionMejoradaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'usuario', 'titulo', 'canal', 'prioridad', 'leido', 'enviado', 'fecha_creacion')
    list_filter = ('tipo', 'canal', 'prioridad', 'leido', 'enviado', 'fecha_creacion')
    search_fields = ('usuario__username', 'titulo', 'mensaje')
    readonly_fields = ('fecha_creacion', 'fecha_envio', 'fecha_lectura')
    
    fieldsets = (
        ('Información de la Notificación', {
            'fields': ('tipo', 'titulo', 'mensaje')
        }),
        ('Configuración', {
            'fields': ('canal', 'prioridad')
        }),
        ('Usuario y Objeto', {
            'fields': ('usuario', 'content_type', 'object_id')
        }),
        ('Estado y Seguimiento', {
            'fields': ('leido', 'enviado', 'fecha_envio', 'fecha_lectura')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['enviar_notificaciones', 'marcar_leidas']
    
    @admin.action(description='Enviar notificaciones seleccionadas')
    def enviar_notificaciones(self, request, queryset):
        for notificacion in queryset:
            if not notificacion.enviado:
                notificacion.enviar_notificacion()
        self.message_user(request, f"Se han enviado {queryset.count()} notificaciones.")
    
    @admin.action(description='Marcar como leídas')
    def marcar_leidas(self, request, queryset):
        for notificacion in queryset:
            if not notificacion.leido:
                notificacion.marcar_leida()
        self.message_user(request, f"Se han marcado {queryset.count()} notificaciones como leídas.")


# ---------------------
# ADMINISTRACIÓN DE NOTIFICACIONES BÁSICAS
# ---------------------
@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'leido', 'fecha_creacion')
    list_filter = ('leido', 'fecha_creacion')
    search_fields = ('titulo', 'mensaje', 'usuario__username')
    readonly_fields = ('fecha_creacion',)
    
    fieldsets = (
        ('Notificación', {
            'fields': ('titulo', 'mensaje', 'usuario')
        }),
        ('Estado', {
            'fields': ('leido',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )


# ---------------------
# ADMINISTRACIÓN DE REPORTES
# ---------------------
@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'administrador', 'fecha_generacion')
    list_filter = ('tipo', 'fecha_generacion')
    search_fields = ('tipo', 'descripcion', 'administrador__username')
    readonly_fields = ('fecha_generacion',)
    
    fieldsets = (
        ('Información del Reporte', {
            'fields': ('tipo', 'descripcion', 'administrador')
        }),
        ('Archivo', {
            'fields': ('archivo',)
        }),
        ('Fechas', {
            'fields': ('fecha_generacion',),
            'classes': ('collapse',)
        }),
    )


# ---------------------
# ADMINISTRACIÓN DE HISTORIAL DE ACCIONES
# ---------------------
@admin.register(HistorialAccion)
class HistorialAccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'accion', 'fecha')
    list_filter = ('fecha',)
    search_fields = ('usuario__username', 'accion', 'detalle')
    readonly_fields = ('fecha',)
    
    fieldsets = (
        ('Acción', {
            'fields': ('usuario', 'accion', 'detalle')
        }),
        ('Fechas', {
            'fields': ('fecha',),
            'classes': ('collapse',)
        }),
    )


# ---------------------
# ADMINISTRACIÓN DE SORTEOS DE RIFAS
# ---------------------
@admin.register(SorteoRifa)
class SorteoRifaAdmin(admin.ModelAdmin):
    list_display = ('rifa', 'ticket_ganador', 'fecha_sorteo')
    list_filter = ('fecha_sorteo',)
    search_fields = ('rifa__titulo', 'ticket_ganador__usuario__username')
    readonly_fields = ('fecha_sorteo',)
    
    fieldsets = (
        ('Sorteo', {
            'fields': ('rifa', 'ticket_ganador')
        }),
        ('Evidencia', {
            'fields': ('evidencia',)
        }),
        ('Fechas', {
            'fields': ('fecha_sorteo',),
            'classes': ('collapse',)
        }),
    )


# ---------------------
# ADMINISTRACIÓN DE TURNOS DE SAN
# ---------------------
@admin.register(TurnoSan)
class TurnoSanAdmin(admin.ModelAdmin):
    list_display = ('numero_turno', 'san', 'participante', 'cumplido', 'fecha_asignacion')
    list_filter = ('cumplido', 'fecha_asignacion')
    search_fields = ('san__nombre', 'participante__usuario__username')
    readonly_fields = ('fecha_asignacion',)
    
    fieldsets = (
        ('Turno', {
            'fields': ('numero_turno', 'san', 'participante')
        }),
        ('Estado', {
            'fields': ('cumplido',)
        }),
        ('Fechas', {
            'fields': ('fecha_asignacion',),
            'classes': ('collapse',)
        }),
    )


# ---------------------
# ADMINISTRACIÓN DE MENSAJES
# ---------------------
@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('remitente', 'destinatario', 'asunto', 'leido', 'fecha_envio')
    list_filter = ('leido', 'fecha_envio')
    search_fields = ('remitente__username', 'destinatario__username', 'asunto', 'contenido')
    readonly_fields = ('fecha_envio',)
    
    fieldsets = (
        ('Mensaje', {
            'fields': ('remitente', 'destinatario', 'asunto', 'contenido')
        }),
        ('Estado', {
            'fields': ('leido',)
        }),
        ('Fechas', {
            'fields': ('fecha_envio',),
            'classes': ('collapse',)
        }),
    )


# ---------------------
# CONFIGURACIÓN DEL ADMIN
# ---------------------
admin.site.site_header = "Administración del Sistema de Rifas y Sanes"
admin.site.site_title = "Rifas y Sanes Admin"
admin.site.index_title = "Panel de Administración"