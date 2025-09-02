# serializers.py
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import (
    CustomUser, Factura, Rifa, Ticket, San, ParticipacionSan, 
    Cupo, Comment, SystemLog, PagoSimulado, NotificacionMejorada,
    Notificacion, Reporte, HistorialAccion, SorteoRifa, TurnoSan, Mensaje
)

# ---------------------
# SERIALIZERS DE USUARIO
# ---------------------
class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer para usuarios con información básica"""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'rol', 'foto_perfil']
        read_only_fields = ['id', 'rol']


class CustomUserDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para usuarios"""
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'rol',
            'phone_number', 'address', 'date_of_birth', 'cedula', 'oficio',
            'foto_perfil', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


# ---------------------
# SERIALIZERS DE RIFA
# ---------------------
class RifaSerializer(serializers.ModelSerializer):
    """Serializer para rifas"""
    organizador = CustomUserSerializer(read_only=True)
    ganador = CustomUserSerializer(read_only=True)
    tickets_vendidos = serializers.ReadOnlyField()
    porcentaje_vendido = serializers.ReadOnlyField()
    
    class Meta:
        model = Rifa
        fields = [
            'id', 'titulo', 'descripcion', 'premio', 'precio_ticket', 
            'total_tickets', 'tickets_disponibles', 'tickets_vendidos',
            'porcentaje_vendido', 'fecha_inicio', 'fecha_fin', 'organizador',
            'estado', 'ganador', 'imagen', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'tickets_disponibles']


class RifaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear rifas"""
    class Meta:
        model = Rifa
        fields = [
            'titulo', 'descripcion', 'premio', 'precio_ticket', 'total_tickets',
            'fecha_fin', 'imagen'
        ]


class RifaDetailSerializer(RifaSerializer):
    """Serializer detallado para rifas con tickets"""
    tickets = serializers.SerializerMethodField()
    
    def get_tickets(self, obj):
        tickets = obj.tickets.filter(activo=True)
        return TicketSerializer(tickets, many=True, read_only=True).data


# ---------------------
# SERIALIZERS DE TICKET
# ---------------------
class TicketSerializer(serializers.ModelSerializer):
    """Serializer para tickets"""
    rifa = RifaSerializer(read_only=True)
    usuario = CustomUserSerializer(read_only=True)
    factura = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Ticket
        fields = [
            'id', 'codigo', 'numero', 'rifa', 'usuario', 'fecha_compra',
            'precio_pagado', 'activo', 'factura'
        ]
        read_only_fields = ['id', 'codigo', 'fecha_compra']


class TicketCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear tickets"""
    class Meta:
        model = Ticket
        fields = ['rifa', 'usuario', 'precio_pagado']


# ---------------------
# SERIALIZERS DE SAN
# ---------------------
class SanSerializer(serializers.ModelSerializer):
    """Serializer para sanes"""
    organizador = CustomUserSerializer(read_only=True)
    cupos_disponibles = serializers.ReadOnlyField()
    porcentaje_ocupado = serializers.ReadOnlyField()
    
    class Meta:
        model = San
        fields = [
            'id', 'nombre', 'descripcion', 'precio_total', 'numero_cuotas',
            'precio_cuota', 'total_participantes', 'participantes_actuales',
            'cupos_disponibles', 'porcentaje_ocupado', 'frecuencia_pago',
            'tipo', 'estado', 'organizador', 'fecha_inicio', 'fecha_fin',
            'imagen', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'participantes_actuales']


class SanCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear sanes"""
    class Meta:
        model = San
        fields = [
            'nombre', 'descripcion', 'precio_total', 'numero_cuotas',
            'total_participantes', 'frecuencia_pago', 'tipo', 'fecha_fin', 'imagen'
        ]


class SanDetailSerializer(SanSerializer):
    """Serializer detallado para sanes con participaciones"""
    participaciones = serializers.SerializerMethodField()
    
    def get_participaciones(self, obj):
        participaciones = obj.participaciones.filter(activa=True)
        return ParticipacionSanSerializer(participaciones, many=True, read_only=True).data


# ---------------------
# SERIALIZERS DE PARTICIPACIÓN
# ---------------------
class ParticipacionSanSerializer(serializers.ModelSerializer):
    """Serializer para participaciones en sanes"""
    san = SanSerializer(read_only=True)
    usuario = CustomUserSerializer(read_only=True)
    cuotas_pendientes = serializers.ReadOnlyField()
    monto_pendiente = serializers.ReadOnlyField()
    
    class Meta:
        model = ParticipacionSan
        fields = [
            'id', 'san', 'usuario', 'fecha_inscripcion', 'orden_cobro',
            'activa', 'cuotas_pagadas', 'fecha_ultima_cuota',
            'cuotas_pendientes', 'monto_pendiente'
        ]
        read_only_fields = ['id', 'fecha_inscripcion']


class ParticipacionSanCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear participaciones"""
    class Meta:
        model = ParticipacionSan
        fields = ['san', 'usuario', 'orden_cobro']


# ---------------------
# SERIALIZERS DE CUPO
# ---------------------
class CupoSerializer(serializers.ModelSerializer):
    """Serializer para cupos"""
    san = SanSerializer(read_only=True)
    participacion = ParticipacionSanSerializer(read_only=True)
    factura = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Cupo
        fields = [
            'id', 'san', 'participacion', 'numero_semana', 'fecha_vencimiento',
            'estado', 'asignado', 'monto_cuota', 'fecha_pago', 'factura'
        ]
        read_only_fields = ['id']


class CupoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear cupos"""
    class Meta:
        model = Cupo
        fields = ['san', 'numero_semana', 'monto_cuota', 'fecha_vencimiento']


# ---------------------
# SERIALIZERS DE FACTURA
# ---------------------
class FacturaSerializer(serializers.ModelSerializer):
    """Serializer para facturas"""
    usuario = CustomUserSerializer(read_only=True)
    tipo_contenido = serializers.SerializerMethodField()
    
    class Meta:
        model = Factura
        fields = [
            'id', 'codigo', 'usuario', 'tipo_contenido', 'monto_total', 
            'monto_pagado', 'estado_pago', 'metodo_pago', 'fecha_emision', 
            'fecha_vencimiento', 'comprobante_pago', 'notas'
        ]
        read_only_fields = ['id', 'codigo', 'fecha_emision']
    
    def get_tipo_contenido(self, obj):
        return obj.get_tipo_contenido()


class FacturaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear facturas"""
    class Meta:
        model = Factura
        fields = [
            'usuario', 'content_type', 'object_id', 'monto_total', 
            'metodo_pago', 'fecha_vencimiento', 'notas'
        ]


# ---------------------
# SERIALIZERS DE PAGO SIMULADO
# ---------------------
class PagoSimuladoSerializer(serializers.ModelSerializer):
    """Serializer para pagos simulados"""
    usuario = CustomUserSerializer(read_only=True)
    factura = FacturaSerializer(read_only=True)
    
    class Meta:
        model = PagoSimulado
        fields = [
            'id', 'codigo_transaccion', 'usuario', 'factura', 'metodo_pago',
            'monto', 'moneda', 'estado', 'referencia_externa', 'fecha_procesamiento',
            'tiempo_procesamiento', 'intentos', 'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'codigo_transaccion', 'fecha_creacion']


class PagoSimuladoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear pagos simulados"""
    class Meta:
        model = PagoSimulado
        fields = ['factura', 'metodo_pago', 'monto', 'moneda']


# ---------------------
# SERIALIZERS DE COMMENT
# ---------------------
class CommentSerializer(serializers.ModelSerializer):
    """Serializer para comentarios"""
    usuario = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'usuario', 'content_type', 'object_id', 'comentario', 
            'fecha_creacion', 'activo'
        ]
        read_only_fields = ['id', 'fecha_creacion']


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear comentarios"""
    class Meta:
        model = Comment
        fields = ['content_type', 'object_id', 'usuario', 'comentario']


# ---------------------
# SERIALIZERS DE NOTIFICACIÓN MEJORADA
# ---------------------
class NotificacionMejoradaSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones mejoradas"""
    usuario = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = NotificacionMejorada
        fields = [
            'id', 'usuario', 'tipo', 'titulo', 'mensaje', 'estado',
            'fecha_creacion', 'fecha_lectura', 'datos_adicionales'
        ]
        read_only_fields = ['id', 'fecha_creacion']


class NotificacionMejoradaCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear notificaciones"""
    class Meta:
        model = NotificacionMejorada
        fields = ['usuario', 'tipo', 'titulo', 'mensaje', 'datos_adicionales']
