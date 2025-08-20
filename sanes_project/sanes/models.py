# sanes/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from django.core.mail import send_mail
from datetime import date
from django.db import models
from django.utils import timezone
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
import uuid
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django import forms

# ---------------------
# FACTURA DIGITAL
# ---------------------
class Factura(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Sirve para Rifas o SANES
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    codigo = models.CharField(max_length=20, unique=True, editable=False)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado_pago = models.CharField(max_length=20, choices=[
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('cancelled', 'Cancelado')
    ], default='pending')
    metodo_pago = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.codigo:
            prefijo = 'RIFA' if self.content_type.model == 'rifa' else 'SAN'
            self.codigo = f"{prefijo}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Factura {self.codigo} - {self.usuario.username}"


# ---------------------
# TICKETS DE RIFA
# ---------------------
class TicketRifa(models.Model):
    rifa = models.ForeignKey("Raffle", on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    codigo_ticket = models.CharField(max_length=20, unique=True, editable=False)
    fecha_compra = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.codigo_ticket:
            self.codigo_ticket = f"TCK-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket {self.codigo_ticket} - {self.usuario.username}"


# ---------------------
# PARTICIPANTES DE SAN
# ---------------------
class ParticipanteSan(models.Model):
    san = models.ForeignKey('San', on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    orden_cobro = models.PositiveIntegerField()
    estado_cobro = models.CharField(max_length=20, choices=[
        ('pending', 'Pendiente'),
        ('received', 'Recibido')
    ], default='pending')

    def __str__(self):
        return f"{self.usuario.username} - Orden {self.orden_cobro}"


# ---------------------
# APORTES DE SAN
# ---------------------
class Aporte(models.Model):
    participante = models.ForeignKey(ParticipanteSan, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_aporte = models.DateTimeField(auto_now_add=True)
    estado_pago = models.CharField(max_length=20, choices=[
        ('pending', 'Pendiente'),
        ('paid', 'Pagado')
    ], default='pending')

    def __str__(self):
        return f"Aporte de {self.participante.usuario.username} - {self.monto}"

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Número de Teléfono")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")
    cedula = models.CharField(max_length=20, blank=True, null=True)
    oficio = models.CharField(max_length=100, blank=True, null=True)
    rol = models.CharField(max_length=20, choices=[('usuario', 'Usuario'), ('administrador', 'Administrador')], default='usuario')
    foto_perfil = models.ImageField(
        upload_to='photo_profiles/',
        blank=True,
        null=True,
        default='photo_profiles/default_avatar.png'
    )

    # Es suficiente con tener una sola definición de estos campos
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="custom_user_groups_set",
        related_query_name="custom_user_group",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_permissions_set",
        related_query_name="custom_user_permission",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.email or self.username


class CambiarFotoPerfilForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['foto_perfil']

class San(models.Model):
    PAYMENT_FREQUENCIES = [
        ('mensual', 'Mensual'),
        ('quincenal', 'Quincenal'),
    ]

    name = models.CharField(max_length=255)
    organizador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sanes_organizados', null=True, blank=True)
    fecha_inicio = models.DateField(default=date.today)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    num_cuotas = models.PositiveIntegerField()
    payment_frequency = models.CharField(max_length=10, choices=PAYMENT_FREQUENCIES, default='mensual')
    type_of_san = models.CharField(max_length=255, choices=[('ahorro', 'Ahorro'), ('producto', 'Producto')])
    image = models.ImageField(upload_to='products/')
    total_participantes = models.PositiveIntegerField(default=1)
    cuota = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    cuota = models.DecimalField(max_digits=10, decimal_places=2)
    total_boletos = models.IntegerField(default=100)
    fecha_fin = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Cierre")
    image = models.ImageField(upload_to='sanes_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_participantes = models.IntegerField()
    total_participantes_actuales = models.IntegerField(default=0)

    @property
    def cupos_disponibles(self):
        return self.total_participantes - self.total_participantes_actuales

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.cuota:
            if self.payment_frequency == 'mensual':
                self.cuota = self.total_price / self.num_cuotas
            elif self.payment_frequency == 'quincenal':
                self.cuota = self.total_price / (self.num_cuotas * 2)
        super(San, self).save(*args, **kwargs)

    def cupos_disponibles(self):
        return self.total_participantes - self.cupos.filter(asignado=True).count()

User = get_user_model()

class TicketSan(models.Model):
    san = models.ForeignKey(San, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    numero = models.PositiveIntegerField()
    codigo_unico = models.CharField(max_length=100, unique=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.codigo_unico:
            # Generar un código único usando UUID
            self.codigo_unico = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket {self.numero} - {self.usuario} ({self.san})"

class Raffle(models.Model):
    description = models.TextField()
    prize_name = models.CharField(max_length=200)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    num_cuotas = models.PositiveIntegerField()
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_fin = models.DateTimeField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_raffles')
    status = models.CharField(max_length=50, default='Active')
    image = models.ImageField(upload_to='raffle_images/', blank=True, null=True)
    ganador = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def seleccionar_ganador(self):
        tickets = TicketRifa.objects.filter(rifa=self)
        if tickets.exists():
            ganador_ticket = random.choice(tickets)
            self.ganador = ganador_ticket.usuario
            self.save()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('raffle_detail', args=[str(self.id)])

class Image(models.Model):
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name='images', verbose_name="Rifa")
    image = models.ImageField(upload_to='raffle_images/', verbose_name="Archivo de Imagen")

    def __str__(self):
        return f"Imagen para {self.raffle.title}"

class Comment(models.Model):
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, verbose_name="Rifa")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuario")
    comment = models.TextField(verbose_name="Comentario")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"

    def __str__(self):
        return f"Comentario de {self.user.username} en {self.raffle.title}"

# Modelo para los tickets de la rifa
class RaffleTicket(models.Model):
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name='tickets')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='raffle_tickets')
    purchase_date = models.DateTimeField(auto_now_add=True)
    ticket_number = models.CharField(max_length=50) # O un campo entero, si se prefieres

    def __str__(self):
        return f"Ticket {self.ticket_number} for {self.raffle.title}"

class Cupo(models.Model):
    ESTADO_CHOICES = [
        ('pendiente_confirmacion', 'Pendiente de Confirmación'),
        ('confirmado', 'Confirmado'),
        ('rechazado', 'Rechazado'),
    ]

    # ¡CORRECCIÓN CRÍTICA! Usar settings.AUTH_USER_MODEL
    participante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    san = models.ForeignKey('San', related_name='cupos', on_delete=models.CASCADE)
    numero_semana = models.PositiveIntegerField()
    asignado = models.BooleanField(default=False)
    metodo_pago = models.CharField(max_length=20, blank=True, null=True)
    comprobante_pago = models.ImageField(upload_to='comprobantes/', blank=True, null=True)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='pendiente_confirmacion')

    def save(self, *args, **kwargs):
        if not self.asignado and self.san.cupos_disponibles() <= 0:
            raise ValueError("No hay cupos disponibles para este SAN.")

        if self.pk is not None:
            old_cupo = Cupo.objects.get(pk=self.pk)
            if old_cupo.estado != self.estado:
                self.notify_user()

        super(Cupo, self).save(*args, **kwargs)

    def notify_user(self):
        subject = ""
        message = ""
        if self.estado == 'confirmado':
            subject = "Confirmación de Pago"
            message = f"Hola {self.participante.username or self.participante.email}, tu pago ha sido confirmado para el SAN {self.san.name}."
        elif self.estado == 'rechazado':
            subject = "Pago Rechazado"
            message = f"Hola {self.participante.username or self.participante.email}, tu pago ha sido rechazado para el SAN {self.san.name}. Por favor, contáctanos para más información."

        if subject and message:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.participante.email],
                fail_silently=False,
            )

    def __str__(self):
        return f'Cupo {self.numero_semana} para el SAN {self.san.name}'


class Order(models.Model):
    # ¡CORRECCIÓN CRÍTICA! Usar settings.AUTH_USER_MODEL
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, null=True, blank=True)
    san = models.ForeignKey(San, on_delete=models.CASCADE, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username or self.user.email}"


class Ticket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    ticket_number = models.CharField(max_length=100)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    issued_at = models.DateTimeField(auto_now_add=True)
    # ¡Campo 'cupo' añadido si es necesario!
    cupo = models.ForeignKey('Cupo', on_delete=models.CASCADE, null=True, blank=True)

class Participacion(models.Model):
    # ¡CORRECCIÓN CRÍTICA! Usar settings.AUTH_USER_MODEL
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    san = models.ForeignKey(San, on_delete=models.CASCADE)
    fecha_ultima_cuota = models.DateField(null=True, blank=True)
    cuotas_pagadas = models.IntegerField(default=0)

    def fecha_proxima_cuota(self):
        hoy = date.today()
        proxima_fecha = None

        if self.san.payment_frequency == 'mensual':
            if hoy.day < 15:
                proxima_fecha = date(hoy.year, hoy.month, 15)
            else:
                if hoy.month == 12:
                    proxima_fecha = date(hoy.year + 1, 1, 15)
                else:
                    proxima_fecha = date(hoy.year, hoy.month + 1, 15)

        elif self.san.payment_frequency == 'quincenal':
            if hoy.day < 15:
                proxima_fecha = date(hoy.year, hoy.month, 15)
            elif hoy.day == 15:
                import calendar
                try:
                    proxima_fecha = date(hoy.year, hoy.month, 30)
                except ValueError:
                    if hoy.month == 12:
                        proxima_fecha = date(hoy.year + 1, 1, 15)
                    else:
                        proxima_fecha = date(hoy.year, hoy.month + 1, 15)
            else:
                if hoy.month == 12:
                    proxima_fecha = date(hoy.year + 1, 1, 15)
                else:
                    proxima_fecha = date(hoy.year, hoy.month + 1, 15)

        return proxima_fecha

    def cuota_a_pagar(self):
        return self.san.total_price / self.san.num_cuotas

    def __str__(self):
        return f"Participacion de {self.user.username or self.user.email} en {self.san.name}"


class Pago(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('rechazado', 'Rechazado'),
    ]

    cupo = models.ForeignKey('Cupo', on_delete=models.CASCADE)
    # ¡CORRECCIÓN CRÍTICA! Usar settings.AUTH_USER_MODEL
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_pago = models.DateField(auto_now_add=True)
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=20, blank=True, null=True)
    comprobante_pago = models.ImageField(upload_to='comprobantes/', blank=True, null=True)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='pendiente')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Pago de {self.usuario.username or self.usuario.email} por {self.monto_pagado} en {self.fecha_pago}"