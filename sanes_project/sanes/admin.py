# sanes/admin.py
from django.contrib import admin
from .models import Cupo, Order, Ticket, CustomUser, Pago, San # Importa todos los modelos necesarios

# --- 1. Registro de CustomUser ---
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'rol')
    list_filter = ('is_staff', 'rol')
    search_fields = ('email', 'first_name', 'last_name')

# --- 2. Registro de Cupo ---
@admin.register(Cupo)
class CupoAdmin(admin.ModelAdmin):
    list_display = ('san', 'participante', 'numero_semana', 'asignado', 'estado')
    list_filter = ('estado', 'san')
    search_fields = ('participante__email', 'san__name')

    actions = ['confirmar_pago', 'rechazar_pago']

    @admin.action(description='Confirmar pago seleccionado')
    def confirmar_pago(self, request, queryset):
        queryset.update(estado='confirmado')
        self.message_user(request, "Pago confirmado con éxito.")

    @admin.action(description='Rechazar pago seleccionado')
    def rechazar_pago(self, request, queryset):
        queryset.update(estado='rechazado')
        self.message_user(request, "Pago rechazado con éxito.")

# --- 3. Registro de Order ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'san', 'total_price', 'created_at')
    list_filter = ('created_at', 'san')

# --- 4. Registro de Ticket ---
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    # ¡Nombres de campo corregidos! 'cupo' debería estar en el modelo Ticket.
    list_display = ('id', 'order', 'ticket_number', 'amount_paid', 'issued_at', 'cupo')
    list_filter = ('order', 'cupo') # 'cupo' ahora es un campo válido para filtrar

# --- 5. Registro de Pago ---
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'cupo', 'monto_pagado', 'fecha_pago', 'estado')
    list_filter = ('estado', 'usuario')
    search_fields = ('usuario__email',)