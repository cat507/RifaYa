# sanes/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    CustomUser, Factura, Rifa, Ticket, San, ParticipacionSan, 
    Cupo, Orden, Pago, Comentario, Imagen
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
        queryset.filter(estado_pago='pendiente').update(estado_pago='vencido')
        self.message_user(request, "Facturas vencidas han sido marcadas.")


# ---------------------
# ADMINISTRACIÓN DE RIFAS
# ---------------------
@admin.register(Rifa)
class RifaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'organizador', 'precio_ticket', 'tickets_vendidos', 'total_tickets', 'estado', 'fecha_inicio', 'fecha_fin')
    list_filter = ('estado', 'fecha_inicio', 'fecha_fin')
    search_fields = ('titulo', 'descripcion', 'organizador__email', 'organizador__username')
    readonly_fields = ('created_at', 'updated_at', 'tickets_disponibles')
    
    def tickets_vendidos(self, obj):
        """Retorna la cantidad de tickets vendidos"""
        return obj.tickets_vendidos()
    tickets_vendidos.short_description = 'Tickets Vendidos'
    
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
        self.message_user(request, "Ganadores han sido seleccionados para las rifas activas.")


# ---------------------
# ADMINISTRACIÓN DE TICKETS
# ---------------------
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'numero', 'rifa', 'usuario', 'precio_pagado', 'fecha_compra', 'activo')
    list_filter = ('activo', 'fecha_compra', 'rifa__estado')
    search_fields = ('codigo', 'numero', 'rifa__titulo', 'usuario__email', 'usuario__username')
    readonly_fields = ('codigo', 'fecha_compra')
    
    fieldsets = (
        ('Información del Ticket', {
            'fields': ('codigo', 'numero', 'rifa', 'usuario')
        }),
        ('Información de Compra', {
            'fields': ('precio_pagado', 'fecha_compra', 'activo')
        }),
        ('Facturación', {
            'fields': ('factura',)
        }),
    )
    
    actions = ['activar_tickets', 'desactivar_tickets']
    
    @admin.action(description='Activar tickets seleccionados')
    def activar_tickets(self, request, queryset):
        queryset.update(activo=True)
        self.message_user(request, f"{queryset.count()} tickets han sido activados.")
    
    @admin.action(description='Desactivar tickets seleccionados')
    def desactivar_tickets(self, request, queryset):
        queryset.update(activo=False)
        self.message_user(request, f"{queryset.count()} tickets han sido desactivados.")


# ---------------------
# ADMINISTRACIÓN DE SANES
# ---------------------
@admin.register(San)
class SanAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'organizador', 'tipo', 'precio_total', 'numero_cuotas', 'precio_cuota', 'participantes_actuales', 'total_participantes', 'estado')
    list_filter = ('tipo', 'estado', 'frecuencia_pago', 'fecha_inicio', 'fecha_fin')
    search_fields = ('nombre', 'descripcion', 'organizador__email', 'organizador__username')
    readonly_fields = ('created_at', 'updated_at', 'participantes_actuales')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'tipo', 'imagen')
        }),
        ('Configuración Financiera', {
            'fields': ('precio_total', 'numero_cuotas', 'precio_cuota', 'frecuencia_pago')
        }),
        ('Participantes', {
            'fields': ('total_participantes', 'participantes_actuales')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin')
        }),
        ('Organización', {
            'fields': ('organizador', 'estado')
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
    list_display = ('usuario', 'san', 'orden_cobro', 'cuotas_pagadas', 'fecha_ultima_cuota', 'activa')
    list_filter = ('activa', 'san__estado', 'san__tipo')
    search_fields = ('usuario__email', 'usuario__username', 'san__nombre')
    readonly_fields = ('fecha_inscripcion',)
    
    fieldsets = (
        ('Participación', {
            'fields': ('usuario', 'san', 'orden_cobro', 'activa')
        }),
        ('Seguimiento de Cuotas', {
            'fields': ('cuotas_pagadas', 'fecha_ultima_cuota', 'fecha_inscripcion')
        }),
    )
    
    actions = ['activar_participaciones', 'desactivar_participaciones']
    
    @admin.action(description='Activar participaciones seleccionadas')
    def activar_participaciones(self, request, queryset):
        queryset.update(activa=True)
        self.message_user(request, f"{queryset.count()} participaciones han sido activadas.")
    
    @admin.action(description='Desactivar participaciones seleccionadas')
    def desactivar_participaciones(self, request, queryset):
        queryset.update(activa=False)
        self.message_user(request, f"{queryset.count()} participaciones han sido desactivadas.")


# ---------------------
# ADMINISTRACIÓN DE CUPOS
# ---------------------
@admin.register(Cupo)
class CupoAdmin(admin.ModelAdmin):
    list_display = ('numero_semana', 'san', 'get_participante', 'estado', 'asignado', 'monto_cuota', 'fecha_vencimiento', 'fecha_pago')
    list_filter = ('estado', 'asignado', 'san__estado', 'fecha_vencimiento')
    search_fields = ('san__nombre', 'participacion__usuario__email', 'participacion__usuario__username')
    readonly_fields = ('numero_semana', 'san', 'monto_cuota')
    
    fieldsets = (
        ('Información del Cupo', {
            'fields': ('numero_semana', 'san', 'monto_cuota', 'fecha_vencimiento')
        }),
        ('Asignación', {
            'fields': ('participacion', 'asignado', 'estado')
        }),
        ('Pago', {
            'fields': ('fecha_pago', 'factura')
        }),
    )
    
    actions = ['asignar_cupos', 'liberar_cupos', 'marcar_pagados', 'marcar_vencidos']
    
    def get_participante(self, obj):
        if obj.participacion and obj.participacion.usuario:
            return obj.participacion.usuario.get_full_name_or_username()
        return "Sin asignar"
    get_participante.short_description = 'Participante'
    
    @admin.action(description='Asignar cupos seleccionados')
    def asignar_cupos(self, request, queryset):
        queryset.filter(estado='disponible').update(estado='asignado', asignado=True)
        self.message_user(request, "Cupos han sido asignados.")
    
    @admin.action(description='Liberar cupos seleccionados')
    def liberar_cupos(self, request, queryset):
        queryset.update(estado='disponible', asignado=False, participacion=None, factura=None)
        self.message_user(request, "Cupos han sido liberados.")
    
    @admin.action(description='Marcar como pagados')
    def marcar_pagados(self, request, queryset):
        queryset.update(estado='pagado')
        self.message_user(request, "Cupos han sido marcados como pagados.")
    
    @admin.action(description='Marcar como vencidos')
    def marcar_vencidos(self, request, queryset):
        queryset.filter(estado='disponible').update(estado='vencido')
        self.message_user(request, "Cupos vencidos han sido marcados.")


# ---------------------
# ADMINISTRACIÓN DE ÓRDENES
# ---------------------
@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'usuario', 'get_tipo_contenido', 'total', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion', 'fecha_actualizacion')
    search_fields = ('codigo', 'usuario__email', 'usuario__username')
    readonly_fields = ('codigo', 'fecha_creacion', 'fecha_actualizacion')
    
    def get_tipo_contenido(self, obj):
        """Retorna el tipo de contenido de la orden"""
        return obj.get_tipo_contenido()
    get_tipo_contenido.short_description = 'Tipo de Contenido'
    
    fieldsets = (
        ('Información de la Orden', {
            'fields': ('codigo', 'usuario', 'content_type', 'object_id')
        }),
        ('Información Financiera', {
            'fields': ('subtotal', 'impuestos', 'total')
        }),
        ('Estado', {
            'fields': ('estado', 'notas')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion')
        }),
    )
    
    actions = ['confirmar_ordenes', 'cancelar_ordenes', 'completar_ordenes']
    
    @admin.action(description='Confirmar órdenes seleccionadas')
    def confirmar_ordenes(self, request, queryset):
        for orden in queryset:
            orden.confirmar()
        self.message_user(request, f"{queryset.count()} órdenes han sido confirmadas.")
    
    @admin.action(description='Cancelar órdenes seleccionadas')
    def cancelar_ordenes(self, request, queryset):
        for orden in queryset:
            orden.cancelar()
        self.message_user(request, f"{queryset.count()} órdenes han sido canceladas.")
    
    @admin.action(description='Completar órdenes seleccionadas')
    def completar_ordenes(self, request, queryset):
        for orden in queryset:
            orden.completar()
        self.message_user(request, f"{queryset.count()} órdenes han sido completadas.")


# ---------------------
# ADMINISTRACIÓN DE PAGOS
# ---------------------
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'usuario', 'get_tipo_contenido', 'monto', 'metodo_pago', 'estado', 'fecha_pago')
    list_filter = ('estado', 'metodo_pago', 'fecha_pago')
    search_fields = ('codigo', 'usuario__email', 'usuario__username')
    readonly_fields = ('codigo', 'fecha_pago')
    
    def get_tipo_contenido(self, obj):
        """Retorna el tipo de contenido del pago"""
        return obj.get_tipo_contenido()
    get_tipo_contenido.short_description = 'Tipo de Contenido'
    
    fieldsets = (
        ('Información del Pago', {
            'fields': ('codigo', 'usuario', 'content_type', 'object_id')
        }),
        ('Información Financiera', {
            'fields': ('monto', 'metodo_pago', 'estado')
        }),
        ('Documentos', {
            'fields': ('comprobante_pago', 'notas')
        }),
        ('Relaciones', {
            'fields': ('orden', 'factura')
        }),
    )
    
    actions = ['confirmar_pagos', 'rechazar_pagos', 'cancelar_pagos']
    
    @admin.action(description='Confirmar pagos seleccionados')
    def confirmar_pagos(self, request, queryset):
        for pago in queryset:
            pago.confirmar()
        self.message_user(request, f"{queryset.count()} pagos han sido confirmados.")
    
    @admin.action(description='Rechazar pagos seleccionados')
    def rechazar_pagos(self, request, queryset):
        for pago in queryset:
            pago.rechazar()
        self.message_user(request, f"{queryset.count()} pagos han sido rechazados.")
    
    @admin.action(description='Cancelar pagos seleccionados')
    def cancelar_pagos(self, request, queryset):
        for pago in queryset:
            pago.cancelar()
        self.message_user(request, f"{queryset.count()} pagos han sido cancelados.")


# ---------------------
# ADMINISTRACIÓN DE COMENTARIOS
# ---------------------
@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'get_tipo_contenido', 'comentario_corto', 'fecha_creacion', 'activo')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('usuario__email', 'usuario__username', 'comentario')
    readonly_fields = ('fecha_creacion',)
    
    fieldsets = (
        ('Comentario', {
            'fields': ('usuario', 'content_type', 'object_id', 'comentario')
        }),
        ('Estado', {
            'fields': ('activo', 'fecha_creacion')
        }),
    )
    
    actions = ['activar_comentarios', 'desactivar_comentarios']
    
    def get_tipo_contenido(self, obj):
        """Retorna el tipo de contenido del comentario"""
        if obj.content_type:
            return obj.content_type.model_class().__name__
        return "Sin tipo"
    get_tipo_contenido.short_description = 'Tipo de Contenido'
    
    def comentario_corto(self, obj):
        return obj.comentario[:100] + "..." if len(obj.comentario) > 100 else obj.comentario
    comentario_corto.short_description = 'Comentario'
    
    @admin.action(description='Activar comentarios seleccionados')
    def activar_comentarios(self, request, queryset):
        queryset.update(activo=True)
        self.message_user(request, f"{queryset.count()} comentarios han sido activados.")
    
    @admin.action(description='Desactivar comentarios seleccionados')
    def desactivar_comentarios(self, request, queryset):
        queryset.update(activo=False)
        self.message_user(request, f"{queryset.count()} comentarios han sido desactivados.")


# ---------------------
# ADMINISTRACIÓN DE IMÁGENES
# ---------------------
@admin.register(Imagen)
class ImagenAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'get_tipo_contenido', 'orden', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'orden', 'fecha_creacion')
    search_fields = ('titulo', 'descripcion')
    readonly_fields = ('fecha_creacion',)
    
    fieldsets = (
        ('Imagen', {
            'fields': ('imagen', 'titulo', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('content_type', 'object_id', 'orden', 'activa')
        }),
        ('Timestamps', {
            'fields': ('fecha_creacion',)
        }),
    )
    
    actions = ['activar_imagenes', 'desactivar_imagenes']
    
    def get_tipo_contenido(self, obj):
        """Retorna el tipo de contenido de la imagen"""
        if obj.content_type:
            return obj.content_type.model_class().__name__
        return "Sin tipo"
    get_tipo_contenido.short_description = 'Tipo de Contenido'
    
    @admin.action(description='Activar imágenes seleccionadas')
    def activar_imagenes(self, request, queryset):
        queryset.update(activa=True)
        self.message_user(request, f"{queryset.count()} imágenes han sido activadas.")
    
    @admin.action(description='Desactivar imágenes seleccionadas')
    def desactivar_imagenes(self, request, queryset):
        queryset.update(activa=False)
        self.message_user(request, f"{queryset.count()} imágenes han sido desactivadas.")


# ---------------------
# CONFIGURACIÓN DEL ADMIN
# ---------------------
admin.site.site_header = "Administración del Sistema de Rifas y Sanes"
admin.site.site_title = "Rifas y Sanes Admin"
admin.site.index_title = "Panel de Administración"