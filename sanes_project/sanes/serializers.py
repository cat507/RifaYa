# serializers.py
from rest_framework import serializers
from .models import San, Cupo, Order, Ticket, CustomUser, Participacion, Pago

class CupoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cupo
        fields = ['id', 'participante', 'san', 'numero_semana', 'asignado', 'metodo_pago', 
                  'comprobante_pago', 'estado']

class SanSerializer(serializers.ModelSerializer):
    cupos = CupoSerializer(many=True, read_only=True)  # Incluir los cupos relacionados
    class Meta:
        model = San
        fields = ['id', 'name', 'organizador', 'fecha_inicio', 'total_price', 'num_cuotas', 
                  'payment_frequency', 'type_of_san', 'image', 'total_participantes', 
                  'cuota', 'cupos']  # Añadimos 'cupos' como campo relacionado

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'san', 'total_price', 'created_at']

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id', 'order', 'ticket_number', 'amount_paid', 'issued_at']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'user', 'cedula', 'oficio', 'telefono']

class ParticipacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participacion
        fields = ['id', 'user', 'san', 'fecha_ultima_cuota', 'cuotas_pagadas']

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = ['id', 'cupo', 'usuario', 'fecha_pago', 'monto_pagado', 'metodo_pago', 
                  'comprobante_pago', 'estado', 'order']
