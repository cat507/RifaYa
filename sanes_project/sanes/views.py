from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import random

from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response


from rest_framework.views import APIView
from rest_framework.response import Response

from .forms import CustomUserCreationForm, CustomLoginForm, RaffleForm, SanForm, ConfirmPurchaseForm
from .models import (
    San, Raffle, Order, Ticket, Cupo,
    Participacion, Pago,
    CustomUser, # Asumiendo que CustomUser es tu modelo de usuario
)
from .serializers import SanSerializer, CupoSerializer
from .backends import EmailOrUsernameModelBackend

from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from .forms import CustomLoginForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import San, Participacion
from django.contrib.auth.decorators import login_required
from datetime import date
from django.shortcuts import render, get_object_or_404
from .models import San, Participacion, Pago
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.shortcuts import render
from .models import Participacion, Pago
from .forms import RaffleForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from .forms import RaffleForm
from .models import Raffle, San, Ticket, Participacion, CustomUser
import uuid
import random
from django.contrib.contenttypes.models import ContentType
from .models import TicketRifa, Factura
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import San, TicketSan
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import CambiarFotoPerfilForm

@login_required
def cambiar_foto_perfil(request):
    if request.method == 'POST':
        form = CambiarFotoPerfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')  # O a donde quieras redirigir
    else:
        form = CambiarFotoPerfilForm(instance=request.user)

    return render(request, 'cambiar_foto_perfil.html', {'form': form})

def buy_raffle_tickets(request, raffle_id):
    ...
    factura = Factura.objects.create(
        usuario=request.user,
        concepto=f"Compra de {cantidad} tickets para {raffle.title}",
        monto=raffle.ticket_price * cantidad
    )
    for _ in range(cantidad):
        TicketRifa.objects.create(
            usuario=request.user,
            rifa=raffle,
            factura=factura
        )
    messages.success(request, f"Compra realizada con éxito. ID Factura: {factura.identificador_unico}")
    ...

def comprar_ticket(request, rifa_id):
    rifa = get_object_or_404(Rifa, id=rifa_id)
    ticket = TicketRifa.objects.create(rifa=rifa, usuario=request.user)
    Factura.objects.create(
        usuario=request.user,
        content_type=ContentType.objects.get_for_model(rifa),
        object_id=rifa.id,
        monto_total=rifa.precio_ticket,
        estado_pago='paid'
    )
    return redirect('factura_detail', codigo=ticket.codigo_ticket)

def asignar_beneficiario(san):
    # Encuentra al próximo que no haya cobrado
    beneficiario = ParticipanteSan.objects.filter(san=san, estado_cobro='pending').order_by('orden').first()
    if beneficiario:
        beneficiario.estado_cobro = 'received'
        beneficiario.save()
        return beneficiario
    return None



def elegir_ganador(rifa_id):
    tickets = list(TicketRifa.objects.filter(rifa_id=rifa_id))
    if not tickets:
        return None
    ganador = random.choice(tickets)
    return ganador.usuario

def generar_codigo_factura(prefijo):
    return f"{prefijo}-{uuid.uuid4().hex[:8].upper()}"

@login_required
def create_san(request):
    if request.method == 'POST':
        form = SanForm(request.POST, request.FILES)
        if form.is_valid():
            san = form.save(commit=False)
            san.organizer = request.user
            san.save()
            messages.success(request, 'SAN creado exitosamente.')
            return redirect('san_detail', san_id=san.id)
    else:
        form = SanForm()

    return render(request, 'create_san.html', {'form': form})

@login_required
def user_profile_view(request):
    return render(request, 'user_profile_view.html')

# --- Funciones Auxiliares ---
def user_is_not_authenticated(user):
    return not user.is_authenticated

def get_sort_date(item):
    """
    Función auxiliar para obtener la fecha de un objeto San o Raffle.
    Asegura que todo se convierta a un objeto datetime con zona horaria (aware).
    """
    if isinstance(item, San):
        naive_dt = datetime.combine(item.fecha_fin, datetime.min.time())
        # Convierte el datetime 'naive' a 'aware'
        return timezone.make_aware(naive_dt)
    elif isinstance(item, Raffle):
        return item.draw_date
    return timezone.now()

@login_required
def cambiar_foto_perfil(request):
    if request.method == 'POST' and request.FILES.get('foto_perfil'):
        nueva_foto = request.FILES['foto_perfil']
        request.user.foto_perfil = nueva_foto
        request.user.save()
        messages.success(request, "Tu foto de perfil se actualizó correctamente.")
    return redirect('user_profile')  # Ajusta si tu vista de perfil se llama diferente

# --- Vistas principales ---
def home(request):
    # Obtener solo algunas rifas (por ejemplo, las últimas 4)
    sanes = San.objects.all().order_by('-fecha_inicio')[:4]
    return render(request, 'home.html', {'sanes': sanes})

def san_list(request):
    query = request.GET.get('q')
    sort_by = request.GET.get('sort_by', 'closing_date_desc')
    status_filter = request.GET.get('status', 'all')

    sanes = list(San.objects.all())
    raffles = list(Raffle.objects.all())
    all_items = sanes + raffles

    # Asigna un tipo de item a cada objeto
    for item in all_items:
        if isinstance(item, Raffle):
            item.item_type = 'raffle'
        else:
            item.item_type = 'san'

    if query:
        all_items = [
            item for item in all_items
            if (hasattr(item, 'name') and query.lower() in item.name.lower()) or
               (hasattr(item, 'title') and query.lower() in item.title.lower()) or
               (hasattr(item, 'prize_name') and query.lower() in item.prize_name.lower())
        ]

    now = timezone.now().date()
    
    if status_filter == 'active':
        all_items = [
            item for item in all_items
            if (hasattr(item, 'fecha_fin') and (item.fecha_fin.date() if isinstance(item.fecha_fin, datetime) else item.fecha_fin) >= now)
        ]
    elif status_filter == 'finished':
        all_items = [
            item for item in all_items
            if (hasattr(item, 'fecha_fin') and (item.fecha_fin.date() if isinstance(item.fecha_fin, datetime) else item.fecha_fin) < now)
        ]

    if sort_by == 'price_asc':
        all_items = sorted(all_items, key=lambda item: item.total_price if hasattr(item, 'total_price') else 0, reverse=False)
    elif sort_by == 'price_desc':
        all_items = sorted(all_items, key=lambda item: item.total_price if hasattr(item, 'total_price') else 0, reverse=True)
    elif sort_by == 'closing_date_asc':
        all_items = sorted(all_items, key=lambda item: item.fecha_fin.date() if isinstance(item.fecha_fin, datetime) else item.fecha_fin, reverse=False)
    elif sort_by == 'closing_date_desc':
        all_items = sorted(all_items, key=lambda item: item.fecha_fin.date() if isinstance(item.fecha_fin, datetime) else item.fecha_fin, reverse=True)
    
    paginator = Paginator(all_items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'sort_by': sort_by,
        'status_filter': status_filter,
    }
    return render(request, 'san_list.html', context)

def raffle_detail(request, raffle_id):
    raffle = get_object_or_404(Raffle, pk=raffle_id)

    tickets_sold = Ticket.objects.filter(order__raffle=raffle).count()
    tickets_available = raffle.num_cuotas - tickets_sold

    # Alias para la plantilla (coincidir con lo que espera el HTML)
    raffle.title = raffle.prize_name
    raffle.ticket_price = raffle.total_price / raffle.num_cuotas if raffle.num_cuotas else 0
    raffle.total_tickets = raffle.num_cuotas
    raffle.draw_date = raffle.fecha_fin  # <-- clave para el contador

    now = timezone.now()
    if raffle.draw_date > now:
        countdown_timedelta = raffle.draw_date - now
    else:
        countdown_timedelta = timedelta(0)

    context = {
        'raffle': raffle,
        'tickets_available': tickets_available,
        'countdown_days': countdown_timedelta.days,
        'countdown_hours': countdown_timedelta.seconds // 3600,
        'countdown_minutes': (countdown_timedelta.seconds % 3600) // 60,
        'countdown_seconds': countdown_timedelta.seconds % 60,
    }
    return render(request, 'raffle_detail.html', context)

def buy_raffle_tickets(request, raffle_id):
    raffle = get_object_or_404(Raffle, pk=raffle_id)
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 0))
            if quantity > 0:
                total_price = quantity * raffle.ticket_price
                messages.success(request, f"Has comprado {quantity} ticket(s) por un total de ${total_price}. ¡Buena suerte!")
                return redirect('raffle_detail', raffle_id=raffle.id)
            else:
                messages.error(request, "La cantidad de tickets debe ser al menos 1.")
                return redirect('raffle_detail', raffle_id=raffle.id)
        except (ValueError, TypeError):
            messages.error(request, "Cantidad de tickets inválida.")
            return redirect('raffle_detail', raffle_id=raffle.id)
    
    return redirect('raffle_detail', raffle_id=raffle.id)

@login_required
def create_raffle(request):
    if request.method == 'POST':
        form = RaffleForm(request.POST, request.FILES)
        if form.is_valid():
            raffle = form.save(commit=False)
            raffle.organizer = request.user
            raffle.save()
            messages.success(request, 'Rifa creada con éxito.')
            # Redirección correcta después de guardar
            return redirect('san_list') 
        else:
            # IMPRIME LOS ERRORES DEL FORMULARIO PARA DEPURAR
            print(form.errors)
            # Continúa a renderizar el formulario con los errores
    else:
        form = RaffleForm()

    context = {
        'form': form,
    }
    return render(request, 'create_raffle.html', context)

def mis_sanes(request):
    if request.user.is_authenticated:
        participaciones = Participacion.objects.filter(user=request.user)
    else:
        participaciones = None

    return render(request, 'mis_sanes.html', {
        'participaciones': participaciones,
    })

@login_required
def san_detail(request, san_id):
    san = get_object_or_404(San, pk=san_id)
    participantes = TicketSan.objects.filter(san=san).select_related('usuario')
    participaciones = list(Participacion.objects.filter(san=san).order_by('id'))
    num_participantes_activos = len(participaciones)
    cuota_a_pagar = san.cuota or (san.total_price / san.num_cuotas if san.num_cuotas else 0)

    participantes_con_datos = []
    frecuencia_semanal = timedelta(weeks=1)

    for index, participacion in enumerate(participaciones):
        cupos = Cupo.objects.filter(participante=participacion.user, san=san)
        pagos_realizados = Pago.objects.filter(cupo__in=cupos, estado='confirmado').exists()

        estado_pago = 'Paid' if pagos_realizados else 'Pending'

        fecha_desembolso = (san.fecha_inicio + (index * frecuencia_semanal)) if san.fecha_inicio else None
        fecha_desembolso_formateada = fecha_desembolso.strftime("%B %d, %Y") if fecha_desembolso else 'N/A'

        participantes_con_datos.append({
            'nombre': participacion.user.get_full_name() or participacion.user.username,
            'estado_pago': estado_pago,
            'fecha_desembolso': fecha_desembolso_formateada,
        })

    context = {
        'san': san,
        'participantes': participantes_con_datos,
        'cuota_a_pagar': cuota_a_pagar,
        'num_participantes_activos': num_participantes_activos,
    }
    return render(request, 'san_detail.html', {
        'san': san,
        'participantes': participantes
    })

@login_required
def my_contributions_view(request):
    user_participaciones = Participacion.objects.filter(user=request.user).order_by('-id')
    user_pagos = Pago.objects.filter(participante=request.user).order_by('-id')

    context = {
        'participaciones': user_participaciones,
        'pagos': user_pagos,
    }
    return render(request, 'my_contributions.html', context)

@login_required
def generar_ticket_san(request, san_id):
    san = get_object_or_404(San, id=san_id)

    # Cupos disponibles
    numeros_ocupados = TicketSan.objects.filter(san=san).values_list('numero', flat=True)
    posibles_numeros = [n for n in range(1, san.total_participantes + 1) if n not in numeros_ocupados]

    if not posibles_numeros:
        messages.error(request, "No hay cupos disponibles para este SAN.")
        return redirect('san_detail', san_id=san.id)

    numero_ticket = random.choice(posibles_numeros)
    codigo_ticket = str(uuid.uuid4())[:8]

    TicketSan.objects.create(
        san=san,
        usuario=request.user,
        numero=numero_ticket,
        codigo_unico=codigo_ticket
    )

    messages.success(request, f"¡Ticket generado! Número: {numero_ticket} | Código: {codigo_ticket}")
    return redirect('san_detail', san_id=san.id)

@property
def cupos_disponibles(self):
    return self.total_participantes - self.tickets.count()

def buy_san(request, san_id):
    san = get_object_or_404(San, id=san_id)
    cupos_asignados = san.cupos.filter(asignado=True).count()
    total_participantes = san.total_participantes
    if cupos_asignados < total_participantes:
        cupos_disponibles = san.cupos.filter(asignado=False).exclude(numero_semana=1)
        if cupos_disponibles.exists():
            cupo_asignado = random.choice(cupos_disponibles)
            cupo_asignado.participante = request.user
            cupo_asignado.asignado = True
            cupo_asignado.save()
            success_message = "Cupo asignado exitosamente."
            messages.success(request, success_message)
            return redirect('confirm_purchase', san_id=san_id)
        else:
            error_message = "No hay cupos disponibles en este momento."
            messages.error(request, error_message)
    else:
        error_message = "No hay cupos disponibles para este SAN."
        messages.error(request, error_message)
    return redirect('san_detail', san_id=san_id)

def asignar_cupo_aleatorio(san_id, usuario):
    san = get_object_or_404(San, pk=san_id)
    cupos_disponibles = san.cupos.filter(asignado=False).exclude(numero_semana=1)
    if cupos_disponibles.exists():
        cupo_asignado = random.choice(cupos_disponibles)
        cupo_asignado.participante = usuario
        cupo_asignado.asignado = True
        cupo_asignado.save()
    else:
        pass # Lógica en caso de que no haya cupos disponibles

def confirmar_compra(request, san_id):
    san = get_object_or_404(San, pk=san_id)
    tasa_bs = Decimal('90')
    monto_bs = san.cuota
    monto_pesos = monto_bs * tasa_bs
    context = {
        'san': san,
        'monto_pesos': monto_pesos
    }
    return render(request, 'confirm_purchase.html', context)

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    san = order.san
    ticket = Ticket.objects.filter(order=order).first()
    return render(request, 'order_confirmation.html', {
        'order': order,
        'san': san,
        'ticket': ticket
    })

@user_passes_test(user_is_not_authenticated)
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('home')
    else:
        form = CustomLoginForm()
    return render(request, 'account/login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('home')

class SanDetailView(DetailView):
    model = San
    template_name = 'san_detail.html'
    context_object_name = 'san'

    def get_object(self):
        return get_object_or_404(San, id=self.kwargs['id'])

# --- APIs ---
class SanListAPIView(APIView):
    def get(self, request):
        sanes = San.objects.all()
        serializer = SanSerializer(sanes, many=True)
        return Response(serializer.data)

def generar_ticket_san(request, san_id):
    san = get_object_or_404(San, id=san_id)

    # Verificar cupos disponibles
    if san.cupos_disponibles() <= 0:
        messages.error(request, "No hay cupos disponibles para este SAN.")
        return redirect('san_detail', san_id=san.id)

    # Obtener el siguiente número de ticket
    siguiente_numero = (TicketSan.objects.filter(san=san).count() + 1)

    # Crear ticket
    TicketSan.objects.create(
        san=san,
        usuario=request.user,
        numero=siguiente_numero
    )

    messages.success(request, "¡Ticket generado con éxito!")
    return redirect('san_detail', san_id=san.id)

class CupoListAPIView(APIView):
    def get(self, request):
        cupos = Cupo.objects.all()
        serializer = CupoSerializer(cupos, many=True)
        return Response(serializer.data)
    
@api_view(['GET'])
def api_home(request):
    """
    Página de inicio de la API.
    Devuelve una respuesta JSON simple.
    """
    data = {
        'message': 'Bienvenido a la API de Sane y Rifas.',
        'endpoints': {
            'sanes_list': '/api/sanes/',
            'cupos_list': '/api/cupos/',
        }
    }
    return Response(data)

