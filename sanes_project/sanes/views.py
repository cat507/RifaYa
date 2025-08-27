# views.py
# =============================================================================
# VISTAS DEL SISTEMA DE RIFAS Y SANES
# =============================================================================
# 
# IMPORTANTE: Este archivo contiene todas las vistas que manejan formularios.
# 
# POSIBLES PROBLEMAS A VERIFICAR:
# 1. Nombres de campos en formularios deben coincidir con los modelos
# 2. URLs referenciadas deben existir en urls.py
# 3. Templates deben existir en las rutas especificadas
# 4. Permisos y decoradores deben estar correctamente aplicados
# 5. Redirecciones deben apuntar a URLs válidas
# 
# FORMULARIOS UTILIZADOS:
# - CustomUserCreationForm: Registro de usuarios
# - CustomLoginForm: Login de usuarios
# - PerfilForm: Edición de perfil
# - RifaForm: Creación/edición de rifas
# - SanForm: Creación/edición de sanes
# - ParticipacionSanForm: Participación en sanes
# - CupoForm: Gestión de cuotas
# - FacturaForm: Gestión de facturas
# - PagoForm: Gestión de pagos
# - CompraTicketForm: Compra de tickets
# - InscripcionSanForm: Inscripción en sanes
# 
# =============================================================================

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.db.models import Sum, Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse, FileResponse
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta, date
from decimal import Decimal
import uuid
import random
import csv

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status

from .forms import (
    CustomUserCreationForm, CustomLoginForm, RifaForm, SanForm, 
    ParticipacionSanForm, CupoForm, FacturaForm, PagoForm, PerfilForm,
    CompraTicketForm, InscripcionSanForm
)
from .models import (
    CustomUser, Factura, Rifa, Ticket, San, ParticipacionSan, 
    Cupo, Orden, Pago, Comment, Imagen, SorteoRifa, Notificacion, SystemLog
)
from .serializers import (
    RifaSerializer, SanSerializer, TicketSerializer, FacturaSerializer,
    ParticipacionSanSerializer, CupoSerializer, OrdenSerializer, PagoSerializer
)
from .backends import EmailOrUsernameModelBackend

# Importaciones adicionales para vistas específicas
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from django.views.decorators.http import require_POST
import io
from reportlab.pdfgen import canvas

# ---------------------
# FUNCIONES AUXILIARES DE CÁLCULO (Sanes y Rifas)
# ---------------------

def calcular_san_contexto(precio_total: Decimal, total_participantes: int, frecuencia_pago: str, fecha_inicio: date, fecha_fin: date, numero_cuotas: int | None = None):
    """Devuelve métricas de viabilidad para sanes."""
    if not precio_total or not total_participantes or not frecuencia_pago:
        return {}

    # Cuota por periodo: si se proporcionan numero_cuotas se usa, sino se estima mínima de 1
    if numero_cuotas and numero_cuotas > 0:
        cuota_por_participante_por_periodo = (Decimal(precio_total) / Decimal(total_participantes)) / Decimal(numero_cuotas)
        periodos_necesarios = numero_cuotas
    else:
        cuota_por_participante_por_periodo = Decimal(precio_total) / Decimal(total_participantes)
        periodos_necesarios = 1

    # Calcular cantidad de periodos disponibles por rango de fechas
    periodos_disponibles = None
    if fecha_inicio and fecha_fin and fecha_fin > fecha_inicio:
        delta_dias = (fecha_fin - fecha_inicio).days
        if frecuencia_pago == 'diaria':
            periodos_disponibles = delta_dias
        elif frecuencia_pago == 'semanal':
            periodos_disponibles = max(1, delta_dias // 7)
        elif frecuencia_pago == 'quincenal':
            periodos_disponibles = max(1, delta_dias // 14)
        elif frecuencia_pago == 'mensual':
            periodos_disponibles = max(1, delta_dias // 30)

    viable = True
    alertas = []
    if periodos_disponibles is not None and numero_cuotas:
        if numero_cuotas > periodos_disponibles:
            viable = False
            alertas.append('El número de cuotas excede los periodos disponibles entre las fechas indicadas.')

    # Monto aportado total esperado con los parámetros actuales
    monto_aportado_total = (cuota_por_participante_por_periodo * Decimal(total_participantes) * Decimal(periodos_necesarios))
    if monto_aportado_total < Decimal(precio_total):
        viable = False
        alertas.append('Los parámetros no cubren el monto total del san.')

    return {
        'cuota_por_participante_por_periodo': cuota_por_participante_por_periodo.quantize(Decimal('0.01')),
        'periodos_necesarios': periodos_necesarios,
        'periodos_disponibles': periodos_disponibles,
        'viable': viable,
        'alertas': alertas,
    }


def calcular_rifa_contexto(precio_ticket: Decimal, total_tickets: int, valor_premio_monetario: Decimal | None):
    """Devuelve métricas de viabilidad para rifas."""
    if not precio_ticket or not total_tickets:
        return {}

    recaudacion_minima_esperada = Decimal(precio_ticket) * Decimal(total_tickets)
    minimo_participantes_para_cubrir_premio = None
    viable = True
    alertas = []

    if valor_premio_monetario is not None and valor_premio_monetario > 0:
        minimo_participantes_para_cubrir_premio = (Decimal(valor_premio_monetario) / Decimal(precio_ticket)).quantize(Decimal('0.01'))
        if recaudacion_minima_esperada < Decimal(valor_premio_monetario):
            viable = False
            alertas.append('Con los parámetros actuales, no se cubre el valor del premio.')

    return {
        'recaudacion_minima_esperada': recaudacion_minima_esperada.quantize(Decimal('0.01')),
        'minimo_participantes_para_cubrir_premio': minimo_participantes_para_cubrir_premio,
        'viable': viable,
        'alertas': alertas,
    }

# ---------------------
# VISTAS DE AUTENTICACIÓN
# ---------------------
def register_view(request):
    """
    Vista para registro de usuarios.
    Maneja GET (mostrar formulario) y POST (procesar datos).
    """
    if request.method == 'POST':
        # Procesar formulario de registro
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # Crear usuario y hacer login automático
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido al sistema.')
            return redirect('home')
        else:
            # Si hay errores, mostrar mensaje
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        # Mostrar formulario vacío
        form = CustomUserCreationForm()
    
    # Renderizar template con formulario
    return render(request, 'account/register.html', {'form': form})


def login_view(request):
    """
    Vista para login de usuarios.
    Maneja GET (mostrar formulario) y POST (procesar datos).
    """
    if request.method == 'POST':
        # Procesar formulario de login
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            # Intentar autenticar usuario
            user = authenticate(request, username=email, password=password)
            if user is not None:
                # Login exitoso
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.get_full_name_or_username()}!')
                return redirect('home')
            else:
                # Credenciales inválidas
                messages.error(request, 'Credenciales inválidas.')
        else:
            # Si hay errores en el formulario
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        # Mostrar formulario vacío
        form = CustomLoginForm()
    
    # Renderizar template con formulario
    return render(request, 'account/login.html', {'form': form})


def logout_view(request):
    """Vista para logout de usuarios"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')


# ---------------------
# VISTAS PRINCIPALES
# ---------------------
def home(request):
    """Vista principal del sistema"""
    # Obtener rifas y sanes activos
    rifas_activas = Rifa.objects.filter(estado='activa').order_by('-created_at')[:6]
    sanes_activos = San.objects.filter(estado='activo').order_by('-created_at')[:6]
    
    # Estadísticas generales
    total_rifas = Rifa.objects.count()
    total_sanes = San.objects.count()
    total_usuarios = CustomUser.objects.count()
    
    context = {
        'rifas_activas': rifas_activas,
        'sanes_activos': sanes_activos,
        'total_rifas': total_rifas,
        'total_sanes': total_sanes,
        'total_usuarios': total_usuarios,
    }
    
    return render(request, 'home.html', context)


# ---------------------
# VISTAS DE RIFAS
# ---------------------
class RifaListView(ListView):
    """Lista de rifas disponibles"""
    model = Rifa
    template_name = 'raffle/rifa_list.html'
    context_object_name = 'rifas'
    paginate_by = 12
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por estado si se especifica
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Búsqueda por título
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) | 
                Q(descripcion__icontains=search) |
                Q(premio__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = Rifa.ESTADOS_RIFA
        return context


class RifaDetailView(DetailView):
    """Detalle de una rifa específica"""
    model = Rifa
    template_name = 'raffle/raffle_detail.html'
    context_object_name = 'rifa'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rifa = self.get_object()
        
        # Obtener tickets de la rifa
        context['tickets'] = rifa.tickets.all().order_by('numero')
        context['tickets_vendidos'] = rifa.tickets_vendidos()
        context['porcentaje_vendido'] = rifa.porcentaje_vendido()
        
        # Verificar si el usuario actual tiene tickets
        if self.request.user.is_authenticated:
            context['tickets_usuario'] = rifa.tickets.filter(usuario=self.request.user)
        
        return context


class RifaCreateView(LoginRequiredMixin, CreateView):
    """Crear una nueva rifa"""
    model = Rifa
    form_class = RifaForm
    template_name = 'raffle/rifa_create.html'
    success_url = reverse_lazy('rifa_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.get('form')
        if form and form.is_bound:
            precio_ticket = form.data.get('precio_ticket') or form.initial.get('precio_ticket')
            total_tickets = form.data.get('total_tickets') or form.initial.get('total_tickets')
            valor_premio = form.data.get('valor_premio_monetario') or None
            try:
                calc = calcular_rifa_contexto(Decimal(precio_ticket), int(total_tickets), Decimal(valor_premio) if valor_premio else None)
                context['calculos_rifa'] = calc
            except Exception:
                context['calculos_rifa'] = {}
        return context

    def form_valid(self, form):
        form.instance.organizador = self.request.user
        messages.success(self.request, 'Rifa creada exitosamente.')
        return super().form_valid(form)


class RifaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Editar una rifa existente"""
    model = Rifa
    form_class = RifaForm
    template_name = 'raffle/rifa_update.html'
    
    def test_func(self):
        rifa = self.get_object()
        return self.request.user == rifa.organizador or self.request.user.is_superuser
    
    def form_valid(self, form):
        messages.success(self.request, 'Rifa actualizada exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        # Redirigir al detalle de la rifa editada
        return reverse('rifa_detail', kwargs={'pk': self.object.pk})


@login_required
def comprar_ticket_rifa(request, rifa_id):
    """Comprar un ticket de rifa"""
    rifa = get_object_or_404(Rifa, id=rifa_id)
    
    if not rifa.puede_vender_tickets():
        messages.error(request, 'No se pueden comprar tickets para esta rifa.')
        return redirect('rifa_detail', pk=rifa_id)
    
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        
        if cantidad > rifa.tickets_disponibles:
            messages.error(request, 'No hay suficientes tickets disponibles.')
            return redirect('rifa_detail', pk=rifa_id)
        
        # Crear orden y factura
        with transaction.atomic():
            orden = Orden.objects.create(
                usuario=request.user,
                content_type=ContentType.objects.get_for_model(Rifa),
                object_id=rifa.id,
                subtotal=rifa.precio_ticket * cantidad,
                total=rifa.precio_ticket * cantidad,
                estado='pendiente'
            )
            
            factura = Factura.objects.create(
                usuario=request.user,
                content_type=ContentType.objects.get_for_model(Rifa),
                object_id=rifa.id,
                monto_total=rifa.precio_ticket * cantidad,
                estado_pago='pendiente'
            )
            
            # Crear tickets
            for i in range(cantidad):
                ticket = Ticket.objects.create(
                    rifa=rifa,
                    usuario=request.user,
                    precio_pagado=rifa.precio_ticket,
                    factura=factura
                )
            
            # Actualizar tickets disponibles
            rifa.tickets_disponibles -= cantidad
            rifa.save()
        
        messages.success(request, f'Se compraron {cantidad} ticket(s) exitosamente.')
        return redirect('checkout_raffle', rifa_id=rifa_id)
    
    return redirect('rifa_detail', pk=rifa_id)


@login_required
def checkout_raffle(request, rifa_id):
    """Checkout para compra de tickets de rifa"""
    rifa = get_object_or_404(Rifa, id=rifa_id)
    tickets_usuario = rifa.tickets.filter(usuario=request.user).order_by('-fecha_compra')
    
    if not tickets_usuario.exists():
        messages.error(request, 'No tienes tickets para esta rifa.')
        return redirect('rifa_detail', pk=rifa_id)
    
    # Obtener la factura más reciente
    factura = tickets_usuario.first().factura
    
    context = {
        'rifa': rifa,
        'tickets': tickets_usuario,
        'factura': factura,
        'total_pagado': tickets_usuario.aggregate(total=Sum('precio_pagado'))['total'] or 0
    }
    
    return render(request, 'raffle/raffle_checkout.html', context)


# ---------------------
# VISTAS DE SANES
# ---------------------
class SanListView(ListView):
    """Lista de sanes disponibles"""
    model = San
    template_name = 'san/san_list.html'
    context_object_name = 'sanes'
    paginate_by = 12
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtrar por estado si se especifica
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar por tipo si se especifica
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Búsqueda por nombre
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) | 
                Q(descripcion__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = San.ESTADOS_SAN
        context['tipos'] = San.TIPOS_SAN
        return context


class SanDetailView(DetailView):
    """Detalle de un san específico"""
    model = San
    template_name = 'san/san_detail.html'
    context_object_name = 'san'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        san = self.get_object()
        
        # Obtener participaciones del san
        context['participaciones'] = san.participaciones.all().order_by('orden_cobro')
        context['cupos_disponibles'] = san.cupos_disponibles()
        context['porcentaje_ocupado'] = san.porcentaje_ocupado()
        
        # Verificar si el usuario actual participa
        if self.request.user.is_authenticated:
            context['participacion_usuario'] = san.participaciones.filter(usuario=self.request.user).first()
        
        return context


class SanCreateView(LoginRequiredMixin, CreateView):
    """Crear un nuevo san"""
    model = San
    form_class = SanForm
    template_name = 'san/create_san.html'
    success_url = reverse_lazy('san_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context.get('form')
        if form and form.is_bound:
            precio_total = form.data.get('precio_total') or form.initial.get('precio_total')
            total_participantes = form.data.get('total_participantes') or form.initial.get('total_participantes')
            frecuencia_pago = form.data.get('frecuencia_pago') or form.initial.get('frecuencia_pago')
            fecha_inicio = form.data.get('fecha_inicio') or form.initial.get('fecha_inicio')
            fecha_fin = form.data.get('fecha_fin') or form.initial.get('fecha_fin')
            numero_cuotas = form.data.get('numero_cuotas') or form.initial.get('numero_cuotas')
            try:
                fecha_inicio_dt = datetime.fromisoformat(fecha_inicio) if fecha_inicio else None
                fecha_fin_dt = datetime.fromisoformat(fecha_fin) if fecha_fin else None
                calc = calcular_san_contexto(
                    Decimal(precio_total) if precio_total else None,
                    int(total_participantes) if total_participantes else None,
                    frecuencia_pago,
                    fecha_inicio_dt.date() if fecha_inicio_dt else None,
                    fecha_fin_dt.date() if fecha_fin_dt else None,
                    int(numero_cuotas) if numero_cuotas else None,
                )
                context['calculos_san'] = calc
            except Exception:
                context['calculos_san'] = {}
        return context

    def form_valid(self, form):
        form.instance.organizador = self.request.user
        messages.success(self.request, 'San creado exitosamente.')
        return super().form_valid(form)


class SanUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Editar un san existente"""
    model = San
    form_class = SanForm
    template_name = 'san/san_update.html'
    
    def test_func(self):
        san = self.get_object()
        return self.request.user == san.organizador or self.request.user.is_superuser
    
    def form_valid(self, form):
        messages.success(self.request, 'San actualizado exitosamente.')
        return super().form_valid(form)

    def get_success_url(self):
        # Redirigir al detalle del san editado
        return reverse('san_detail', kwargs={'pk': self.object.pk})


@login_required
def inscribirse_san(request, san_id):
    """Inscribirse en un san"""
    san = get_object_or_404(San, id=san_id)
    
    if not san.puede_agregar_participante():
        messages.error(request, 'No se puede inscribir en este san.')
        return redirect('san_detail', pk=san_id)
    
    # Verificar si ya está inscrito
    if san.participaciones.filter(usuario=request.user).exists():
        messages.warning(request, 'Ya estás inscrito en este san.')
        return redirect('san_detail', pk=san_id)
    
    if request.method == 'POST':
        # Crear participación
        participacion = ParticipacionSan.objects.create(
            san=san,
            usuario=request.user,
            orden_cobro=san.participaciones.count() + 1
        )
        
        # Actualizar contador de participantes
        san.participantes_actuales += 1
        san.save()
        
        messages.success(request, 'Te has inscrito exitosamente en el san.')
        return redirect('checkout_san', san_id=san_id)
    
    return redirect('san_detail', pk=san_id)


@login_required
def checkout_san(request, san_id):
    """Checkout para inscripción en san"""
    san = get_object_or_404(San, id=san_id)
    participacion = san.participaciones.filter(usuario=request.user).first()
    
    if not participacion:
        messages.error(request, 'No estás inscrito en este san.')
        return redirect('san_detail', pk=san_id)
    
    # Obtener cuotas del usuario
    cuotas = san.cupos.filter(participacion=participacion).order_by('numero_semana')
    
    context = {
        'san': san,
        'participacion': participacion,
        'cuotas': cuotas,
        'cuotas_pendientes': participacion.cuotas_pendientes(),
        'monto_pendiente': participacion.monto_pendiente()
    }
    
    return render(request, 'san/cuotas_san.html', context)


# ---------------------
# VISTAS DE FACTURAS
# ---------------------
class FacturaListView(LoginRequiredMixin, ListView):
    """Lista de facturas del usuario"""
    model = Factura
    template_name = 'facturas/lista.html'
    context_object_name = 'facturas'
    paginate_by = 10
    ordering = ['-fecha_emision']
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(usuario=self.request.user)


class FacturaDetailView(LoginRequiredMixin, DetailView):
    """Detalle de una factura"""
    model = Factura
    template_name = 'facturas/detalle.html'
    context_object_name = 'factura'
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(usuario=self.request.user)


@login_required
def subir_comprobante_factura(request, factura_id):
    """Subir comprobante de pago para una factura"""
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
    
    if request.method == 'POST':
        comprobante = request.FILES.get('comprobante')
        if comprobante:
            factura.comprobante_pago = comprobante
            factura.estado_pago = 'pendiente'
            factura.save()
            messages.success(request, 'Comprobante subido exitosamente.')
        else:
            messages.error(request, 'Debe seleccionar un archivo.')
    
    return redirect('factura_detail', pk=factura_id)


# ---------------------
# VISTAS DE PAGOS
# ---------------------
@login_required
def pagar_cuota_san(request, cupo_id):
    """Pagar una cuota de san"""
    cupo = get_object_or_404(Cupo, id=cupo_id)
    
    # Verificar que el cupo pertenece al usuario
    if cupo.participacion.usuario != request.user:
        messages.error(request, 'No tienes permisos para pagar este cupo.')
        return redirect('san_detail', pk=cupo.san.id)
    
    if request.method == 'POST':
        metodo_pago = request.POST.get('metodo_pago', 'efectivo')
        
        # Crear factura y pago
        with transaction.atomic():
            factura = Factura.objects.create(
                usuario=request.user,
                content_type=ContentType.objects.get_for_model(Cupo),
                object_id=cupo.id,
                monto_total=cupo.monto_cuota,
                estado_pago='pendiente',
                metodo_pago=metodo_pago
            )
            
            pago = Pago.objects.create(
                usuario=request.user,
                content_type=ContentType.objects.get_for_model(Cupo),
                object_id=cupo.id,
                monto=cupo.monto_cuota,
                estado='pendiente',
                metodo_pago=metodo_pago,
                factura=factura
            )
            
            # Actualizar cupo
            cupo.factura = factura
            cupo.save()
        
        messages.success(request, 'Pago registrado exitosamente. Pendiente de confirmación.')
        return redirect('factura_detail', pk=factura.id)
    
    return redirect('san_detail', pk=cupo.san.id)


# ---------------------
# VISTAS DE PERFIL DE USUARIO
# ---------------------
@login_required
def user_profile(request):
    """Perfil del usuario"""
    user = request.user
    
    # Obtener rifas y sanes del usuario
    rifas_usuario = Rifa.objects.filter(organizador=user)
    sanes_usuario = San.objects.filter(organizador=user)
    
    # Obtener tickets comprados
    tickets_comprados = Ticket.objects.filter(usuario=user).select_related('rifa')
    
    # Obtener participaciones en sanes
    participaciones = ParticipacionSan.objects.filter(usuario=user).select_related('san')
    
    # Calcular estadísticas
    tickets_comprados_count = tickets_comprados.count()
    sanes_participando_count = participaciones.filter(san__estado='activo').count()
    premios_ganados_count = Rifa.objects.filter(ganador=user).count()
    total_gastado = Factura.objects.filter(
        usuario=user,
        estado_pago='confirmado'
    ).aggregate(total=Sum('monto_total'))['total'] or 0
    
    context = {
        'user': user,
        'rifas_usuario': rifas_usuario,
        'sanes_usuario': sanes_usuario,
        'tickets_comprados': tickets_comprados,
        'participaciones': participaciones,
        'tickets_comprados_count': tickets_comprados_count,
        'sanes_participando_count': sanes_participando_count,
        'premios_ganados_count': premios_ganados_count,
        'total_gastado': total_gastado,
    }
    
    return render(request, 'user/profile.html', context)


@login_required
def cambiar_foto_perfil(request):
    """Cambiar foto de perfil"""
    if request.method == 'POST':
        foto = request.FILES.get('foto_perfil')
        if foto:
            request.user.foto_perfil = foto
            request.user.save()
            messages.success(request, 'Foto de perfil actualizada exitosamente.')
        else:
            messages.error(request, 'Debe seleccionar una imagen.')
    
    return redirect('user_profile')


# ---------------------
# VISTAS DE ADMINISTRACIÓN
# ---------------------
@login_required
@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    """Dashboard de administración"""
    # Estadísticas generales
    total_usuarios = CustomUser.objects.count()
    total_rifas = Rifa.objects.count()
    total_sanes = San.objects.count()
    total_facturas = Factura.objects.count()
    
    # Facturas pendientes
    facturas_pendientes = Factura.objects.filter(estado_pago='pendiente').order_by('-fecha_emision')
    
    # Últimas actividades
    ultimas_rifas = Rifa.objects.order_by('-created_at')[:5]
    ultimos_sanes = San.objects.order_by('-created_at')[:5]
    
    context = {
        'total_usuarios': total_usuarios,
        'total_rifas': total_rifas,
        'total_sanes': total_sanes,
        'total_facturas': total_facturas,
        'facturas_pendientes': facturas_pendientes,
        'ultimas_rifas': ultimas_rifas,
        'ultimos_sanes': ultimos_sanes,
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
@login_required
@user_passes_test(lambda u: u.is_superuser)
def confirmar_pago(request, factura_id):
    """Confirmar pago de una factura"""
    factura = get_object_or_404(Factura, id=factura_id)
    
    if request.method == 'POST':
        factura.estado_pago = 'confirmado'
        factura.monto_pagado = factura.monto_total
        factura.save()
        
        # Actualizar pagos relacionados
        pagos = factura.pagos.all()
        for pago in pagos:
            pago.estado = 'confirmado'
            pago.save()
        
        # Si es un cupo, marcarlo como pagado
        if factura.content_type.model == 'cupo':
            cupo = Cupo.objects.get(id=factura.object_id)
            cupo.estado = 'pagado'
            cupo.fecha_pago = date.today()
            cupo.save()
            
            # Actualizar participación
            participacion = cupo.participacion
            participacion.cuotas_pagadas += 1
            participacion.fecha_ultima_cuota = date.today()
            participacion.save()
        
        messages.success(request, 'Pago confirmado exitosamente.')
    
    return redirect('admin_dashboard')


@login_required
@login_required
@user_passes_test(lambda u: u.is_superuser)
def rechazar_pago(request, factura_id):
    """Rechazar pago de una factura"""
    factura = get_object_or_404(Factura, id=factura_id)
    
    if request.method == 'POST':
        factura.estado_pago = 'rechazado'
        factura.save()
        
        # Actualizar pagos relacionados
        pagos = factura.pagos.all()
        for pago in pagos:
            pago.estado = 'rechazado'
            pago.save()
        
        messages.success(request, 'Pago rechazado exitosamente.')
    
    return redirect('admin_dashboard')


# ---------------------
# VISTAS DE REPORTES
# ---------------------
@login_required
@login_required
@user_passes_test(lambda u: u.is_superuser)
def reporte_rifas(request):
    """Reporte de rifas"""
    rifas = Rifa.objects.all().order_by('-created_at')
    
    # Estadísticas
    total_rifas = rifas.count()
    rifas_activas = rifas.filter(estado='activa').count()
    rifas_finalizadas = rifas.filter(estado='finalizada').count()
    total_tickets_vendidos = Ticket.objects.count()
    
    context = {
        'rifas': rifas,
        'total_rifas': total_rifas,
        'rifas_activas': rifas_activas,
        'rifas_finalizadas': rifas_finalizadas,
        'total_tickets_vendidos': total_tickets_vendidos,
    }
    
    return render(request, 'reports/reporte_rifas.html', context)


@login_required
@login_required
@user_passes_test(lambda u: u.is_superuser)
def reporte_sanes(request):
    """Reporte de sanes"""
    sanes = San.objects.all().order_by('-created_at')
    
    # Estadísticas
    total_sanes = sanes.count()
    sanes_activos = sanes.filter(estado='activo').count()
    sanes_finalizados = sanes.filter(estado='finalizado').count()
    total_participantes = ParticipacionSan.objects.count()
    
    context = {
        'sanes': sanes,
        'total_sanes': total_sanes,
        'sanes_activos': sanes_activos,
        'sanes_finalizados': sanes_finalizados,
        'total_participantes': total_participantes,
    }
    
    return render(request, 'reports/reporte_sanes.html', context)


# ---------------------
# VISTAS API (REST Framework)
# ---------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_rifa_list(request):
    """API: Lista de rifas"""
    rifas = Rifa.objects.all()
    serializer = RifaSerializer(rifas, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_rifa_detail(request, pk):
    """API: Detalle de rifa"""
    rifa = get_object_or_404(Rifa, pk=pk)
    serializer = RifaSerializer(rifa)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_san_list(request):
    """API: Lista de sanes"""
    sanes = San.objects.all()
    serializer = SanSerializer(sanes, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_san_detail(request, pk):
    """API: Detalle de san"""
    san = get_object_or_404(San, pk=pk)
    serializer = SanSerializer(san)
    return Response(serializer.data)


# ---------------------
# VISTAS DE ERROR
# ---------------------
def handler404(request, exception):
    """
    Manejo de error 404 - Página no encontrada.
    Renderiza template personalizado o usa template por defecto.
    """
    try:
        return render(request, 'misc/errors/404.html', status=404)
    except:
        # Si no existe el template personalizado, usar template básico
        return render(request, '404.html', status=404)


def handler500(request):
    """
    Manejo de error 500 - Error interno del servidor.
    Renderiza template personalizado o usa template por defecto.
    """
    try:
        return render(request, 'misc/errors/500.html', status=500)
    except:
        # Si no existe el template personalizado, usar template básico
        return render(request, '500.html', status=500)

# ESTE ES UN MENSAJE PARA CURSOR, PARA QUE SEPA QUE A PARTIR DE AQUÍ ES DÓNDE USARA LOS 
# VIEWS PARA GENERAR LAS VISTAS (TEMPLATES) DE LAS PAGINAS, EN SU DEFECTO HARA USO DE LAS VIEWS QUE NECESITE
# DE ARRIBA, PARA SU CONVENIENCIA.

@login_required
def perfil_usuario(request):
    """
    Vista para editar perfil de usuario.
    Maneja GET (mostrar formulario) y POST (procesar datos).
    """
    if request.method == 'POST':
        # Procesar formulario enviado
        form = PerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # Guardar cambios en el perfil
            form.save()
            messages.success(request, "Perfil actualizado correctamente")
            # Redirigir al perfil del usuario, no a la página de edición
            return redirect('user_profile')
        else:
            # Si hay errores, mostrar mensaje
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        # Mostrar formulario vacío con datos actuales
        form = PerfilForm(instance=request.user)
    
    # Renderizar template con formulario (con errores si los hay)
    return render(request, 'usuarios/perfil.html', {'form': form})

@login_required
def lista_rifas(request):
    """Listar rifas activas"""
    rifas = Rifa.objects.filter(estado='activa', fecha_fin__gte=timezone.now())
    return render(request, 'rifas/lista.html', {'rifas': rifas})

@login_required
def detalle_rifa(request, rifa_id):
    """Detalle de una rifa"""
    rifa = get_object_or_404(Rifa, id=rifa_id)
    tickets = rifa.tickets.all()
    return render(request, 'rifas/detalle.html', {'rifa': rifa, 'tickets': tickets})

@login_required
def comprar_ticket(request, rifa_id):
    """
    Vista para comprar ticket de una rifa.
    Usa formulario CompraTicketForm para validación.
    """
    # Obtener la rifa o devolver 404 si no existe
    rifa = get_object_or_404(Rifa, id=rifa_id)
    
    # Verificar si se pueden comprar tickets
    if not rifa.puede_vender_tickets():
        messages.error(request, "No se pueden comprar tickets para esta rifa.")
        return redirect('detalle_rifa', rifa_id=rifa.id)

    if request.method == 'POST':
        # Procesar formulario de compra
        form = CompraTicketForm(request.POST)
        if form.is_valid():
            numero = form.cleaned_data['numero']
            
            # Verificar si el número ya está ocupado
            if Ticket.objects.filter(rifa=rifa, numero=numero).exists():
                messages.error(request, "Este número ya fue comprado.")
            else:
                # Crear ticket y factura en una transacción
                with transaction.atomic():
                    # Crear factura primero
                    factura = Factura.objects.create(
                        usuario=request.user,
                        content_type=ContentType.objects.get_for_model(Rifa),
                        object_id=rifa.id,
                        monto_total=rifa.precio_ticket,
                        estado_pago='pendiente'
                    )
                    
                    # Crear ticket
                    ticket = Ticket.objects.create(
                        rifa=rifa,
                        usuario=request.user,
                        numero=numero,
                        precio_pagado=rifa.precio_ticket,
                        factura=factura
                    )
                    
                    # Actualizar tickets disponibles
                    rifa.tickets_disponibles -= 1
                    rifa.save()
                
                messages.success(request, "Ticket comprado con éxito.")
                return redirect('detalle_rifa', rifa_id=rifa.id)
        else:
            # Si hay errores en el formulario
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        # Mostrar formulario vacío
        form = CompraTicketForm()

    # Renderizar template con formulario
    return render(request, 'rifas/comprar.html', {'rifa': rifa, 'form': form})

@login_required
def historial_rifas(request):
    """Historial de rifas y tickets comprados"""
    tickets = request.user.tickets_comprados.select_related('rifa').order_by('-fecha_compra')
    return render(request, 'rifas/historial.html', {'tickets': tickets})

@login_required
def lista_sanes(request):
    """Listar sanes activos"""
    sanes = San.objects.filter(estado='activo', fecha_fin__gte=date.today())
    return render(request, 'sanes/lista.html', {'sanes': sanes})

@login_required
def detalle_san(request, san_id):
    """Detalle de un san"""
    san = get_object_or_404(San, id=san_id)
    participacion = ParticipacionSan.objects.filter(usuario=request.user, san=san).first()
    return render(request, 'sanes/detalle.html', {'san': san, 'participacion': participacion})

@login_required
def unirse_san(request, san_id):
    """
    Vista para unirse a un san.
    Usa formulario InscripcionSanForm para validación.
    """
    # Obtener el san o devolver 404 si no existe
    san = get_object_or_404(San, id=san_id)
    
    # Verificar si el usuario ya está inscrito
    if ParticipacionSan.objects.filter(usuario=request.user, san=san).exists():
        messages.warning(request, "Ya estás inscrito en este san.")
        return redirect('detalle_san', san_id=san.id)
    
    # Verificar si el san puede aceptar más participantes
    if not san.puede_agregar_participante():
        messages.error(request, "Este san ya no acepta más participantes.")
        return redirect('detalle_san', san_id=san.id)

    if request.method == 'POST':
        # Procesar formulario de inscripción
        form = InscripcionSanForm(request.POST)
        if form.is_valid():
            # Intentar agregar participante
            participacion = san.agregar_participante(request.user)
            if participacion:
                messages.success(request, "Te has unido al san correctamente.")
                return redirect('detalle_san', san_id=san.id)
            else:
                messages.error(request, "No fue posible unirse al san.")
        else:
            # Si hay errores en el formulario
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        # Mostrar formulario vacío
        form = InscripcionSanForm()

    # Renderizar template con formulario
    return render(request, 'sanes/unirse.html', {'san': san, 'form': form})

@login_required
def historial_sanes(request):
    """Historial de participaciones en sanes"""
    participaciones = request.user.participaciones_san.select_related('san').order_by('-fecha_inscripcion')
    return render(request, 'sanes/historial.html', {'participaciones': participaciones})

@login_required
def lista_notificaciones(request):
    """Notificaciones del usuario"""
    notificaciones = request.user.notificaciones.all()
    return render(request, 'usuarios/notificaciones.html', {'notificaciones': notificaciones})

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_superuser)(view_func)

@admin_required
def lista_usuarios(request):
    usuarios = CustomUser.objects.all()
    return render(request, 'admin/usuarios/lista.html', {'usuarios': usuarios})

@admin_required
def detalle_usuario(request, user_id):
    usuario = get_object_or_404(CustomUser, id=user_id)
    return render(request, 'admin/usuarios/detalle.html', {'usuario': usuario})

@admin_required
def crear_rifa(request):
    """
    Vista para crear una nueva rifa (solo administradores).
    Maneja GET (mostrar formulario) y POST (procesar datos).
    """
    if request.method == 'POST':
        # Procesar formulario enviado
        form = RifaForm(request.POST, request.FILES)
        if form.is_valid():
            # Guardar rifa con organizador y estado
            rifa = form.save(commit=False)
            rifa.organizador = request.user
            rifa.estado = 'activa'
            rifa.save()
            messages.success(request, "Rifa creada correctamente.")
            # Redirigir al detalle de la rifa creada
            return redirect('rifa_detail', pk=rifa.id)
        else:
            # Si hay errores, mostrar mensaje
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        # Mostrar formulario vacío
        form = RifaForm()
    
    # Renderizar template con formulario
    return render(request, 'admin/rifas/crear.html', {'form': form})

@admin_required
def finalizar_rifa(request, rifa_id):
    rifa = get_object_or_404(Rifa, id=rifa_id)
    ganador = rifa.seleccionar_ganador()
    if ganador:
        SorteoRifa.objects.create(rifa=rifa, ticket_ganador=rifa.tickets.filter(usuario=ganador).first())
        Notificacion.objects.create(
            usuario=ganador,
            titulo="¡Ganaste la rifa!",
            mensaje=f"Felicidades, ganaste la rifa {rifa.titulo}."
        )
        messages.success(request, f"Rifa finalizada. Ganador: {ganador.get_full_name_or_username()}")
    else:
        messages.error(request, "No se pudo seleccionar un ganador.")
    return redirect('detalle_rifa', rifa_id=rifa.id)

@admin_required
def crear_san(request):
    """
    Vista para crear un nuevo san (solo administradores).
    Maneja GET (mostrar formulario) y POST (procesar datos).
    """
    if request.method == 'POST':
        # Procesar formulario enviado
        form = SanForm(request.POST, request.FILES)
        if form.is_valid():
            # Guardar san con organizador y estado
            san = form.save(commit=False)
            san.organizador = request.user
            san.estado = 'activo'
            san.save()
            messages.success(request, "San creado correctamente.")
            # Redirigir al detalle del san creado
            return redirect('san_detail', pk=san.id)
        else:
            # Si hay errores, mostrar mensaje
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        # Mostrar formulario vacío
        form = SanForm()
    
    # Renderizar template con formulario
    return render(request, 'admin/sanes/crear.html', {'form': form})

@admin_required
def reporte_finanzas(request):
    """Generar reporte de facturas y pagos"""
    facturas = Factura.objects.all()
    total_facturado = facturas.aggregate(Sum('monto_total'))['monto_total__sum'] or 0
    total_pagado = facturas.filter(estado_pago='confirmado').aggregate(Sum('monto_total'))['monto_total__sum'] or 0
    return render(request, 'admin/reportes/finanzas.html', {
        'facturas': facturas,
        'total_facturado': total_facturado,
        'total_pagado': total_pagado,
    })

def admin_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.is_superuser)(view_func)

# ---------------------
# VISTAS EXTRA DE USUARIO
# ---------------------

class CustomPasswordResetView(PasswordResetView):
    """Recuperación de contraseña con allauth o auth de Django"""
    template_name = 'account/password_reset.html'
    email_template_name = 'account/password_reset_email.html'
    form_class = PasswordResetForm
    success_url = reverse_lazy('login')


@login_required
def resultados_rifas(request):
    """Mostrar rifas finalizadas y sus ganadores"""
    rifas_finalizadas = Rifa.objects.filter(estado='finalizada').order_by('-fecha_fin')
    sorteos = SorteoRifa.objects.filter(rifa__in=rifas_finalizadas).select_related('ticket_ganador')
    return render(request, 'rifas/resultados.html', {'sorteos': sorteos})


@login_required
def turnos_san(request, san_id):
    """Mostrar calendario de turnos de cobro de un san"""
    san = get_object_or_404(San, id=san_id)
    participaciones = san.participaciones.order_by('orden_cobro')
    return render(request, 'sanes/turnos.html', {'san': san, 'participaciones': participaciones})


# ---------------------
# VISTAS EXTRA DE ADMINISTRACIÓN
# ---------------------

@admin_required
def enviar_notificacion_global(request):
    """Enviar notificación global a todos los usuarios"""
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        mensaje = request.POST.get('mensaje')
        if titulo and mensaje:
            for user in CustomUser.objects.all():
                Notificacion.objects.create(usuario=user, titulo=titulo, mensaje=mensaje)
            messages.success(request, "Notificación enviada a todos los usuarios.")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Debe ingresar título y mensaje.")
    return render(request, 'admin/notificaciones/enviar.html')


@admin_required
def exportar_reporte_rifas_pdf(request):
    """Exportar reporte de rifas a PDF"""
    rifas = Rifa.objects.all()
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica", 12)
    p.drawString(100, 800, "Reporte de Rifas")
    y = 760
    for rifa in rifas:
        p.drawString(100, y, f"{rifa.titulo} - Estado: {rifa.estado} - Tickets vendidos: {rifa.tickets.count()}")
        y -= 20
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="reporte_rifas.pdf")


@admin_required
def asignar_turnos_san(request, san_id):
    """Permite al admin reordenar turnos de cobro de un san"""
    san = get_object_or_404(San, id=san_id)
    participaciones = san.participaciones.order_by('orden_cobro')
    
    if request.method == 'POST':
        for p in participaciones:
            nuevo_orden = request.POST.get(f"orden_{p.id}")
            if nuevo_orden and nuevo_orden.isdigit():
                p.orden_cobro = int(nuevo_orden)
                p.save()
        messages.success(request, "Turnos reordenados correctamente.")
        return redirect('turnos_san', san_id=san.id)

    return render(request, 'admin/sanes/asignar_turnos.html', {'san': san, 'participaciones': participaciones})

def exportar_logs(request):
    """Exportar logs del sistema a CSV"""
    if not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para acceder a esta función.')
        return redirect('admin_dashboard')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="logs_sistema.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Usuario', 'Acción', 'Nivel', 'Descripción', 'IP', 'Fecha'])
    
    logs = SystemLog.objects.all().order_by('-fecha_creacion')
    for log in logs:
        writer.writerow([
            log.usuario.username if log.usuario else 'Sistema',
            log.get_tipo_accion_display(),
            log.get_nivel_display(),
            log.descripcion,
            log.ip_address,
            log.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response


@login_required
@user_passes_test(lambda u: u.is_superuser)
def cambiar_estado_factura(request, factura_id):
    """Vista para cambiar el estado de una factura (admin)"""
    factura = get_object_or_404(Factura, id=factura_id)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado in ['pendiente', 'confirmado', 'cancelado']:
            factura.estado_pago = nuevo_estado
            if nuevo_estado == 'confirmado' and not factura.fecha_pago:
                factura.fecha_pago = timezone.now()
            factura.save()
            
            # Log de la acción
            log_user_action(
                user=request.user,
                action_type='cambiar_estado_factura',
                description=f'Cambió estado de factura {factura.id} a {nuevo_estado}',
                level='INFO',
                related_object=factura,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'Estado de la factura cambiado a "{nuevo_estado}".')
        else:
            messages.error(request, 'Estado no válido.')
    
    return redirect('admin_factura_list')


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_logs(request):
    """Vista para mostrar logs del sistema (admin)"""
    # Filtros
    action_type = request.GET.get('action_type')
    level = request.GET.get('level')
    user_id = request.GET.get('user')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Query base
    logs = SystemLog.objects.all().select_related('usuario').order_by('-fecha_creacion')
    
    # Aplicar filtros
    if action_type:
        logs = logs.filter(tipo_accion=action_type)
    if level:
        logs = logs.filter(nivel=level)
    if user_id:
        logs = logs.filter(usuario_id=user_id)
    if date_from:
        logs = logs.filter(fecha_creacion__gte=date_from)
    if date_to:
        logs = logs.filter(fecha_creacion__lte=date_to)
    
    # Paginación
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    total_logs = SystemLog.objects.count()
    today_logs = SystemLog.objects.filter(fecha_creacion__date=timezone.now().date()).count()
    week_logs = SystemLog.objects.filter(fecha_creacion__gte=timezone.now() - timedelta(days=7)).count()
    month_logs = SystemLog.objects.filter(fecha_creacion__gte=timezone.now() - timedelta(days=30)).count()
    
    # Usuarios para filtro
    users = CustomUser.objects.filter(logs__isnull=False).distinct()
    
    context = {
        'page_obj': page_obj,
        'total_logs': total_logs,
        'today_logs': today_logs,
        'week_logs': week_logs,
        'month_logs': month_logs,
        'users': users,
        'tipos_accion': SystemLog.TIPOS_ACCION,
        'niveles': SystemLog.NIVELES,
        'filters': {
            'action_type': action_type,
            'level': level,
            'user': user_id,
            'date_from': date_from,
            'date_to': date_to,
        }
    }
    
    return render(request, 'admin/logs.html', context)

# ---------------------
# VISTAS FALTANTES - CLASES BASADAS EN VISTAS
# ---------------------

class MisSanesView(LoginRequiredMixin, ListView):
    """Vista para mostrar los sanes del usuario actual"""
    model = ParticipacionSan
    template_name = 'sanes/mis_sanes.html'
    context_object_name = 'participaciones'
    paginate_by = 10

    def get_queryset(self):
        return ParticipacionSan.objects.filter(
            usuario=self.request.user
        ).select_related('san').order_by('-fecha_inscripcion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todas las participaciones para estadísticas (sin paginación)
        todas_participaciones = ParticipacionSan.objects.filter(
            usuario=self.request.user
        ).select_related('san')
        
        # Estadísticas generales
        context['total_sanes_count'] = todas_participaciones.count()
        context['sanes_activos_count'] = todas_participaciones.filter(san__estado='activo').count()
        
        # Totales financieros
        total_invertido = sum(p.total_pagado for p in todas_participaciones)
        total_pendiente = sum(p.san.precio_total - p.total_pagado for p in todas_participaciones if p.san.estado == 'activo')
        
        context['total_invertido'] = total_invertido
        context['total_pendiente'] = total_pendiente
        
        return context


class MyContributionsView(LoginRequiredMixin, ListView):
    """Vista para mostrar las contribuciones del usuario"""
    model = Cupo
    template_name = 'sanes/my_contributions.html'
    context_object_name = 'contribuciones'
    paginate_by = 15

    def get_queryset(self):
        return Cupo.objects.filter(
            participacion__usuario=self.request.user
        ).select_related('participacion__san').order_by('-fecha_vencimiento')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener todas las contribuciones para estadísticas (sin paginación)
        todas_contribuciones = Cupo.objects.filter(
            participacion__usuario=self.request.user
        ).select_related('participacion__san')
        
        # Estadísticas de cuotas
        context['cuotas_pagadas_count'] = todas_contribuciones.filter(estado='pagado').count()
        context['cuotas_pendientes_count'] = todas_contribuciones.filter(estado='asignado').count()
        
        # Totales financieros
        context['total_pagado'] = todas_contribuciones.filter(estado='pagado').aggregate(
            total=Sum('monto_cuota')
        )['total'] or 0
        
        context['total_pendiente'] = todas_contribuciones.filter(estado='asignado').aggregate(
            total=Sum('monto_cuota')
        )['total'] or 0
        
        # Sanes para filtro
        context['sanes'] = San.objects.filter(
            participaciones__usuario=self.request.user
        ).distinct()
        
        return context


class AdminUserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista para listar usuarios (admin)"""
    model = CustomUser
    template_name = 'admin/user_list.html'
    context_object_name = 'usuarios'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        queryset = CustomUser.objects.all().order_by('-date_joined')
        
        # Filtros
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_usuarios'] = CustomUser.objects.count()
        context['usuarios_activos'] = CustomUser.objects.filter(is_active=True).count()
        return context


class AdminUserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Vista para detalle de usuario (admin)"""
    model = CustomUser
    template_name = 'admin/user_detail.html'
    context_object_name = 'usuario'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.get_object()
        
        # Estadísticas del usuario
        context['rifas_creadas'] = Rifa.objects.filter(organizador=usuario).count()
        context['sanes_creados'] = San.objects.filter(organizador=usuario).count()
        context['tickets_comprados'] = Ticket.objects.filter(usuario=usuario).count()
        context['participaciones_san'] = ParticipacionSan.objects.filter(usuario=usuario).count()
        context['facturas'] = Factura.objects.filter(usuario=usuario).order_by('-fecha_creacion')[:10]
        
        return context


class AdminRifaListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista para listar rifas (admin)"""
    model = Rifa
    template_name = 'admin/rifa_list.html'
    context_object_name = 'rifas'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        queryset = Rifa.objects.all().select_related('organizador').order_by('-created_at')
        
        # Filtros
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(organizador__username__icontains=search)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_rifas'] = Rifa.objects.count()
        context['rifas_activas'] = Rifa.objects.filter(estado='activa').count()
        context['rifas_finalizadas'] = Rifa.objects.filter(estado='finalizada').count()
        return context


class AdminSanListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista para listar sanes (admin)"""
    model = San
    template_name = 'admin/san_list.html'
    context_object_name = 'sanes'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        queryset = San.objects.all().select_related('organizador').order_by('-created_at')
        
        # Filtros
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(organizador__username__icontains=search)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_sanes'] = San.objects.count()
        context['sanes_activos'] = San.objects.filter(estado='activo').count()
        context['sanes_finalizados'] = San.objects.filter(estado='finalizado').count()
        return context


class AdminFacturaListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Vista para listar facturas (admin)"""
    model = Factura
    template_name = 'admin/factura_list.html'
    context_object_name = 'facturas'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        queryset = Factura.objects.all().select_related('usuario').order_by('-fecha_emision')
        
        # Filtros
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado_pago=estado)
        
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(usuario__username__icontains=search) |
                Q(usuario__email__icontains=search)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_facturas'] = Factura.objects.count()
        context['facturas_pendientes'] = Factura.objects.filter(estado_pago='pendiente').count()
        context['facturas_pagadas'] = Factura.objects.filter(estado_pago='confirmado').count()
        context['total_recaudado'] = Factura.objects.filter(estado_pago='confirmado').aggregate(
            total=Sum('monto_total')
        )['total'] or 0
        return context


class AdminReporteView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Vista para reportes administrativos"""
    template_name = 'admin/reportes.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        context['total_usuarios'] = CustomUser.objects.count()
        context['total_rifas'] = Rifa.objects.count()
        context['total_sanes'] = San.objects.count()
        context['total_facturas'] = Factura.objects.count()
        
        # Estadísticas específicas
        context['usuarios_activos'] = CustomUser.objects.filter(is_active=True).count()
        context['rifas_finalizadas'] = Rifa.objects.filter(estado='finalizada').count()
        context['sanes_finalizados'] = San.objects.filter(estado='finalizado').count()
        
        # Estadísticas financieras
        context['total_recaudado'] = Factura.objects.filter(estado_pago='confirmado').aggregate(
            total=Sum('monto_total')
        )['total'] or 0
        
        context['total_pendiente'] = Factura.objects.filter(estado_pago='pendiente').aggregate(
            total=Sum('monto_total')
        )['total'] or 0
        
        # Estadísticas específicas por tipo
        context['total_recaudado_rifas'] = Factura.objects.filter(
            estado_pago='confirmado',
            content_type__model='rifa'
        ).aggregate(total=Sum('monto_total'))['total'] or 0
        
        context['total_recaudado_sanes'] = Factura.objects.filter(
            estado_pago='confirmado',
            content_type__model='san'
        ).aggregate(total=Sum('monto_total'))['total'] or 0
        
        # Actividad reciente
        context['rifas_recientes'] = Rifa.objects.all().order_by('-created_at')[:5]
        context['sanes_recientes'] = San.objects.all().order_by('-created_at')[:5]
        context['usuarios_recientes'] = CustomUser.objects.all().order_by('-date_joined')[:5]
        
        return context


# ---------------------
# VISTAS FALTANTES - FUNCIONES BASADAS EN VISTAS
# ---------------------

@login_required
def historial_pagos_san(request, san_id):
    """Vista para mostrar historial de pagos de un san"""
    san = get_object_or_404(San, id=san_id)
    
    # Verificar que el usuario sea organizador o participante
    if not (request.user == san.organizador or 
            san.participaciones.filter(usuario=request.user).exists()):
        messages.error(request, 'No tienes permisos para ver este historial.')
        return redirect('san_list')
    
    # Obtener pagos del san
    pagos = Pago.objects.filter(
        content_type=ContentType.objects.get_for_model(san),
        object_id=san.id
    ).select_related('usuario').order_by('-fecha_pago')
    
    # Estadísticas
    total_pagado = pagos.aggregate(total=Sum('monto'))['total'] or 0
    total_esperado = san.precio_total
    
    context = {
        'san': san,
        'pagos': pagos,
        'total_pagado': total_pagado,
        'total_esperado': total_esperado,
        'porcentaje_completado': (total_pagado / total_esperado * 100) if total_esperado > 0 else 0
    }
    
    return render(request, 'sanes/historial_pagos.html', context)


@login_required
def adelantar_cuota_san(request, participacion_id):
    """Vista para adelantar cuotas de un san"""
    participacion = get_object_or_404(ParticipacionSan, id=participacion_id, usuario=request.user)
    
    if request.method == 'POST':
        # Obtener cuotas pendientes
        cuotas_pendientes = Cupo.objects.filter(
            participacion=participacion,
            estado='asignado'
        ).order_by('fecha_vencimiento')
        
        if cuotas_pendientes.exists():
            # Tomar la primera cuota pendiente
            cuota = cuotas_pendientes.first()
            
            # Crear factura para el pago adelantado
            factura = Factura.objects.create(
                usuario=request.user,
                monto=cuota.monto_cuota,
                tipo='cuota_san',
                estado='pendiente',
                descripcion=f'Pago adelantado - Cuota {cuota.numero_semana} del San {participacion.san.nombre}'
            )
            
            # Crear orden
            orden = Orden.objects.create(
                usuario=request.user,
                factura=factura,
                monto_total=cuota.monto_cuota,
                estado='pendiente'
            )
            
            messages.success(request, f'Se ha creado una orden para adelantar la cuota {cuota.numero_semana}.')
            return redirect('factura_detail', pk=factura.id)
        else:
            messages.error(request, 'No hay cuotas pendientes para adelantar.')
    
    return redirect('san_detail', pk=participacion.san.id)


@login_required
def factura_pagar(request, factura_id):
    """Vista para pagar una factura"""
    factura = get_object_or_404(Factura, id=factura_id, usuario=request.user)
    
    if request.method == 'POST':
        # Procesar pago
        factura.estado = 'pagada'
        factura.fecha_pago = timezone.now()
        factura.save()
        
        # Si es una factura de cuota, marcar la cuota como pagada
        if factura.tipo == 'cuota_san':
            try:
                orden = factura.orden_set.first()
                if orden:
                    # Buscar la cuota correspondiente
                    cupo = Cupo.objects.filter(
                        participacion__usuario=request.user,
                        monto_cuota=factura.monto,
                        estado='asignado'
                    ).first()
                    
                    if cupo:
                        cupo.estado = 'pagado'
                        cupo.fecha_pago = timezone.now()
                        cupo.save()
                        
                        # Crear registro de pago
                        Pago.objects.create(
                            cupo=cupo,
                            monto=factura.monto,
                            fecha_pago=timezone.now(),
                            metodo_pago='transferencia'
                        )
            except Exception as e:
                messages.warning(request, f'Factura pagada pero hubo un problema al actualizar la cuota: {str(e)}')
        
        messages.success(request, 'Factura pagada exitosamente.')
        return redirect('factura_list')
    
    context = {
        'factura': factura,
        'orden': factura.orden_set.first() if hasattr(factura, 'orden_set') else None
    }
    
    return render(request, 'facturas/pagar.html', context)


# ---------------------
# VISTAS DE COMENTARIOS
# ---------------------

@login_required
def agregar_comentario(request, content_type_id, object_id):
    """Vista para agregar comentarios"""
    if request.method == 'POST':
        content_type = get_object_or_404(ContentType, id=content_type_id)
        model_class = content_type.model_class()
        obj = get_object_or_404(model_class, id=object_id)
        
        texto = request.POST.get('texto')
        if texto:
            Comment.objects.create(
                usuario=request.user,
                content_type=content_type,
                object_id=object_id,
                texto=texto
            )
            messages.success(request, 'Comentario agregado exitosamente.')
        else:
            messages.error(request, 'El comentario no puede estar vacío.')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def eliminar_comentario(request, comentario_id):
    """Vista para eliminar comentarios"""
    comentario = get_object_or_404(Comment, id=comentario_id)
    
    # Verificar permisos
    if request.user == comentario.usuario or request.user.is_superuser:
        comentario.delete()
        messages.success(request, 'Comentario eliminado exitosamente.')
    else:
        messages.error(request, 'No tienes permisos para eliminar este comentario.')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))


# ---------------------
# VISTAS DE NOTIFICACIONES
# ---------------------

@login_required
def notificaciones_usuario(request):
    """Vista para mostrar notificaciones del usuario"""
    notificaciones = Notificacion.objects.filter(
        usuario=request.user
    ).order_by('-fecha_creacion')
    
    context = {
        'notificaciones': notificaciones
    }
    
    return render(request, 'notificaciones/lista.html', context)


@login_required
def marcar_notificacion_leida(request, notificacion_id):
    """Vista para marcar notificación como leída"""
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, usuario=request.user)
    notificacion.leido = True
    notificacion.save()
    
    return JsonResponse({'success': True})


@login_required
def marcar_todas_leidas(request):
    """Vista para marcar todas las notificaciones como leídas"""
    Notificacion.objects.filter(usuario=request.user, leido=False).update(leido=True)
    
    return JsonResponse({'success': True})


@login_required
def obtener_notificaciones_ajax(request):
    """Vista AJAX para obtener notificaciones"""
    notificaciones = Notificacion.objects.filter(
        usuario=request.user,
        leido=False
    ).order_by('-fecha_creacion')[:10]
    
    data = []
    for notif in notificaciones:
        data.append({
            'id': notif.id,
            'titulo': notif.titulo,
            'mensaje': notif.mensaje,
            'fecha': notif.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'tipo': notif.tipo
        })
    
    return JsonResponse({'notificaciones': data})


# ---------------------
# FUNCIÓN AUXILIAR PARA LOGGING
# ---------------------

def log_user_action(user, action_type, description, level='INFO', related_object=None, ip_address=None):
    """Función auxiliar para registrar acciones de usuarios"""
    if not ip_address and hasattr(user, 'request'):
        ip_address = user.request.META.get('REMOTE_ADDR')
    
    SystemLog.objects.create(
        usuario=user,
        tipo_accion=action_type,
        descripcion=description,
        nivel=level,
        objeto_relacionado=related_object,
        ip_address=ip_address or '0.0.0.0'
    )
