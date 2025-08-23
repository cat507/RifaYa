# serializers.py
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import (
    CustomUser, Factura, Rifa, Ticket, San, ParticipacionSan, 
    Cupo, Orden, Pago, Comentario, Imagen
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
# SERIALIZERS DE ORDEN
# ---------------------
class OrdenSerializer(serializers.ModelSerializer):
    """Serializer para órdenes"""
    usuario = CustomUserSerializer(read_only=True)
    tipo_contenido = serializers.SerializerMethodField()
    
    class Meta:
        model = Orden
        fields = [
            'id', 'codigo', 'usuario', 'tipo_contenido', 'fecha_creacion',
            'fecha_actualizacion', 'subtotal', 'impuestos', 'total',
            'estado', 'notas'
        ]
        read_only_fields = ['id', 'codigo', 'fecha_creacion', 'fecha_actualizacion']
    
    def get_tipo_contenido(self, obj):
        return obj.get_tipo_contenido()


class OrdenCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear órdenes"""
    class Meta:
        model = Orden
        fields = [
            'usuario', 'content_type', 'object_id', 'subtotal',
            'impuestos', 'total', 'notas'
        ]


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
# SERIALIZERS DE PAGO
# ---------------------
class PagoSerializer(serializers.ModelSerializer):
    """Serializer para pagos"""
    usuario = CustomUserSerializer(read_only=True)
    orden = OrdenSerializer(read_only=True)
    factura = FacturaSerializer(read_only=True)
    tipo_contenido = serializers.SerializerMethodField()
    
    class Meta:
        model = Pago
        fields = [
            'id', 'codigo', 'usuario', 'tipo_contenido', 'fecha_pago',
            'monto', 'estado', 'metodo_pago', 'comprobante_pago', 'notas',
            'orden', 'factura'
        ]
        read_only_fields = ['id', 'codigo', 'fecha_pago']
    
    def get_tipo_contenido(self, obj):
        return obj.get_tipo_contenido()


class PagoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear pagos"""
    class Meta:
        model = Pago
        fields = [
            'usuario', 'content_type', 'object_id', 'monto', 'estado',
            'metodo_pago', 'comprobante_pago', 'notas', 'orden', 'factura'
        ]


# ---------------------
# SERIALIZERS DE COMENTARIO
# ---------------------
class ComentarioSerializer(serializers.ModelSerializer):
    """Serializer para comentarios"""
    usuario = CustomUserSerializer(read_only=True)
    
    class Meta:
        model = Comentario
        fields = [
            'id', 'usuario', 'comentario', 'fecha_creacion', 'activo'
        ]
        read_only_fields = ['id', 'fecha_creacion']


class ComentarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear comentarios"""
    class Meta:
        model = Comentario
        fields = ['content_type', 'object_id', 'usuario', 'comentario']


# ---------------------
# SERIALIZERS DE IMAGEN
# ---------------------
class ImagenSerializer(serializers.ModelSerializer):
    """Serializer para imágenes"""
    class Meta:
        model = Imagen
        fields = [
            'id', 'imagen', 'titulo', 'descripcion', 'orden', 'activa',
            'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion']


class ImagenCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear imágenes"""
    class Meta:
        model = Imagen
        fields = ['content_type', 'object_id', 'imagen', 'titulo', 'descripcion', 'orden']
