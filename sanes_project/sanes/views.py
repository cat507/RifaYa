# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.db.models import Sum, Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status

from .forms import (
    CustomUserCreationForm, RifaForm, SanForm, 
    ParticipacionSanForm, CupoForm, FacturaForm, PagoForm
)
from .models import (
    CustomUser, Factura, Rifa, Ticket, San, ParticipacionSan, 
    Cupo, Orden, Pago, Comentario, Imagen
)
from .serializers import (
    RifaSerializer, SanSerializer, TicketSerializer, FacturaSerializer,
    ParticipacionSanSerializer, CupoSerializer, OrdenSerializer, PagoSerializer
)
from .backends import EmailOrUsernameModelBackend

# ---------------------
# VISTAS DE AUTENTICACIÓN
# ---------------------
def register_view(request):
    """Vista para registro de usuarios"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido al sistema.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'account/register.html', {'form': form})


def login_view(request):
    """Vista para login de usuarios"""
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido, {user.get_full_name_or_username()}!')
                return redirect('home')
            else:
                messages.error(request, 'Credenciales inválidas.')
    else:
        form = CustomLoginForm()
    
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
    
    return render(request, 'misc/home.html', context)


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
    
    def form_valid(self, form):
        form.instance.organizador = self.request.user
        messages.success(self.request, 'Rifa creada exitosamente.')
        return super().form_valid(form)


class RifaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Editar una rifa existente"""
    model = Rifa
    form_class = RifaForm
    template_name = 'raffle/create_raffle.html'
    
    def test_func(self):
        rifa = self.get_object()
        return self.request.user == rifa.organizador or self.request.user.is_admin()
    
    def form_valid(self, form):
        messages.success(self.request, 'Rifa actualizada exitosamente.')
        return super().form_valid(form)


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
    
    def form_valid(self, form):
        form.instance.organizador = self.request.user
        messages.success(self.request, 'San creado exitosamente.')
        return super().form_valid(form)


class SanUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Editar un san existente"""
    model = San
    form_class = SanForm
    template_name = 'san/mis_sanes.html'
    
    def test_func(self):
        san = self.get_object()
        return self.request.user == san.organizador or self.request.user.is_admin()
    
    def form_valid(self, form):
        messages.success(self.request, 'San actualizado exitosamente.')
        return super().form_valid(form)


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
    template_name = 'orders/factura_list.html'
    context_object_name = 'facturas'
    paginate_by = 10
    ordering = ['-fecha_emision']
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return super().get_queryset()
        return super().get_queryset().filter(usuario=self.request.user)


class FacturaDetailView(LoginRequiredMixin, DetailView):
    """Detalle de una factura"""
    model = Factura
    template_name = 'orders/factura_detail.html'
    context_object_name = 'factura'
    
    def get_queryset(self):
        if self.request.user.is_admin():
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
    
    context = {
        'user': user,
        'rifas_usuario': rifas_usuario,
        'sanes_usuario': sanes_usuario,
        'tickets_comprados': tickets_comprados,
        'participaciones': participaciones,
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
@user_passes_test(lambda u: u.is_admin())
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
@user_passes_test(lambda u: u.is_admin())
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
@user_passes_test(lambda u: u.is_admin())
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
@user_passes_test(lambda u: u.is_admin())
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
@user_passes_test(lambda u: u.is_admin())
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
    """Manejo de error 404"""
    return render(request, 'misc/errors/404.html', status=404)


def handler500(request):
    """Manejo de error 500"""
    return render(request, 'misc/errors/500.html', status=500)

