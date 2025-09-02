# sanes/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django import forms
from datetime import date, timedelta
import uuid
import random
from django.core.exceptions import ValidationError


# ---------------------
# MODELO DE USUARIO UNIFICADO
# ---------------------
class CustomUser(AbstractUser):
    """Usuario personalizado con roles y permisos claros"""
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Número de Teléfono")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")
    cedula = models.CharField(max_length=20, blank=True, null=True, verbose_name="Cédula")
    oficio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Oficio")
    rol = models.CharField(
        max_length=20, 
        choices=[
            ('usuario', 'Usuario'), 
            ('administrador', 'Administrador')
        ], 
        default='usuario',
        verbose_name="Rol"
    )
    foto_perfil = models.ImageField(
        upload_to='photo_profiles/',
        blank=True,
        null=True,
        default='photo_profiles/default_avatar.png',
        verbose_name="Foto de Perfil"
    )

    # Relaciones para evitar conflictos
    groups = models.ManyToManyField(
        Group,
        verbose_name='Grupos',
        blank=True,
        help_text='Los grupos a los que pertenece este usuario.',
        related_name="custom_user_groups_set",
        related_query_name="custom_user_group",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='Permisos de Usuario',
        blank=True,
        help_text='Permisos específicos para este usuario.',
        related_name="custom_user_permissions_set",
        related_query_name="custom_user_permission",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']

    def __str__(self):
        return self.email or self.username

    def is_admin(self):
        """Verifica si el usuario es administrador"""
        return self.rol == 'administrador'

    def get_full_name_or_username(self):
        """Retorna el nombre completo o username como fallback"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username


# ---------------------
# MODELO DE FACTURA UNIFICADO
# ---------------------
class Factura(models.Model):
    """Factura digital que funciona tanto para rifas como para sanes"""
    ESTADOS_PAGO = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('rechazado', 'Rechazado'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('otro', 'Otro'),
    ]
<<<<<<< HEAD
=======
    
    # Campos para compatibilidad con código existente
    TIPOS_CHOICES = [
        ('rifa', 'Rifa'),
        ('san', 'San'),
        ('cuota_san', 'Cuota de San'),
        ('ticket_rifa', 'Ticket de Rifa'),
        ('inscripcion_san', 'Inscripción a San'),
        ('otro', 'Otro'),
    ]
    
    ESTADOS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('vencida', 'Vencida'),
        ('cancelada', 'Cancelada'),
    ]
>>>>>>> 61950c8 (Corrección de error y estado estable)

    # Identificación única
    codigo = models.CharField(max_length=20, unique=True, editable=False, null=True, blank=True, verbose_name="Código de Factura")
    
    # Usuario que genera la factura
    usuario = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        verbose_name="Usuario",
        related_name='facturas'
    )
    
    # Contenido genérico (Rifa o San)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tipo de Contenido")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID del Objeto")
    content_object = GenericForeignKey('content_type', 'object_id')
    
<<<<<<< HEAD
=======
    # Campos para compatibilidad con código existente
    concepto = models.CharField(max_length=255, blank=True, null=True, verbose_name="Concepto")
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Monto")
    tipo = models.CharField(max_length=20, choices=TIPOS_CHOICES, default='otro', verbose_name="Tipo")
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='pendiente', verbose_name="Estado")
    
>>>>>>> 61950c8 (Corrección de error y estado estable)
    # Información de la factura
    fecha_emision = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Emisión")
    fecha_vencimiento = models.DateTimeField(
        verbose_name="Fecha de Vencimiento",
        null=True,
        blank=True
    )
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Monto Total")
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Monto Pagado")
    
    # Estado y método de pago
    estado_pago = models.CharField(
        max_length=20, 
        choices=ESTADOS_PAGO, 
        default='pendiente',
        verbose_name="Estado del Pago"
    )
    metodo_pago = models.CharField(
        max_length=20, 
        choices=METODOS_PAGO, 
        blank=True, 
        null=True,
        verbose_name="Método de Pago"
    )
    
    # Comprobante de pago (para transferencias)
    comprobante_pago = models.ImageField(
        upload_to='comprobantes/', 
        blank=True, 
        null=True,
        verbose_name="Comprobante de Pago"
    )
    
    # Notas adicionales
    notas = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales")
<<<<<<< HEAD
=======
    
    # Campos adicionales para compatibilidad
    fecha_pago = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Pago")
    rifa = models.ForeignKey('Rifa', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Rifa")
    san = models.ForeignKey('San', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="San")
    archivo = models.FileField(upload_to='facturas/', null=True, blank=True, verbose_name="Archivo")
>>>>>>> 61950c8 (Corrección de error y estado estable)

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha_emision']

    def save(self, *args, **kwargs):
        if not self.codigo:
            # Generar código único basado en el tipo de contenido
            if self.content_type.model == 'rifa':
                prefijo = 'RIFA'
            elif self.content_type.model == 'san':
                prefijo = 'SAN'
            else:
                prefijo = 'FACT'
            
            self.codigo = f"{prefijo}-{uuid.uuid4().hex[:8].upper()}"
        
        # Establecer fecha de vencimiento por defecto (30 días)
        if not self.fecha_vencimiento:
            self.fecha_vencimiento = timezone.now() + timedelta(days=30)
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Factura {self.codigo} - {self.usuario.get_full_name_or_username()}"

    def get_tipo_contenido(self):
        """Retorna el tipo de contenido (Rifa o San)"""
        return self.content_type.model_class().__name__

    def get_monto_pendiente(self):
        """Calcula el monto pendiente de pago"""
        return self.monto_total - self.monto_pagado

    def is_pagada(self):
        """Verifica si la factura está completamente pagada"""
        return self.estado_pago == 'confirmado' and self.monto_pagado >= self.monto_total

    def is_vencida(self):
        """Verifica si la factura está vencida"""
        return timezone.now() > self.fecha_vencimiento
<<<<<<< HEAD
=======
    
    # Métodos para compatibilidad con código existente
    @property
    def id_unico(self):
        """Alias para el código de la factura"""
        return self.codigo
    
    def get_estado_display(self):
        """Retorna el estado para compatibilidad"""
        return self.get_estado_pago_display()
>>>>>>> 61950c8 (Corrección de error y estado estable)

    def confirmar_pago(self, monto=None):
        """Confirma el pago de la factura"""
        if monto:
            self.monto_pagado = monto
        self.estado_pago = 'confirmado'
        self.save()

    def rechazar_pago(self):
        """Rechaza el pago de la factura"""
        self.estado_pago = 'rechazado'
        self.save()


# ---------------------
# MODELO DE RIFA UNIFICADO
# ---------------------
class Rifa(models.Model):
    """Modelo unificado para rifas"""
    ESTADOS_RIFA = [
        ('borrador', 'Borrador'),
        ('activa', 'Activa'),
        ('pausada', 'Pausada'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
    ]

    # Información básica
    titulo = models.CharField(max_length=200, blank=True, verbose_name="Título de la Rifa")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    premio = models.CharField(max_length=200, blank=True, verbose_name="Premio")
    
    # Configuración de la rifa
    precio_ticket = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Precio por Ticket")
    total_tickets = models.PositiveIntegerField(default=100, verbose_name="Total de Tickets")
    tickets_disponibles = models.PositiveIntegerField(default=100, verbose_name="Tickets Disponibles")
    
    # Fechas
    fecha_inicio = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Inicio")
    fecha_fin = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Cierre")
    
    # Organizador
    organizador = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='rifas_organizadas',
        verbose_name="Organizador"
    )
    
    # Estado
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS_RIFA, 
        default='borrador',
        verbose_name="Estado"
    )
    
    # Ganador
    ganador = models.ForeignKey(
        CustomUser, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='rifas_ganadas',
        verbose_name="Ganador"
    )
    
    # Imagen
    imagen = models.ImageField(
        upload_to='rifas_images/', 
        blank=True, 
        null=True,
        verbose_name="Imagen de la Rifa"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = 'Rifa'
        verbose_name_plural = 'Rifas'
        ordering = ['-created_at']

    def __str__(self):
        return self.titulo
    
    @property
    def comentarios(self):
        """Retorna los comentarios activos de la rifa"""
        return Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            activo=True
        )

    def get_absolute_url(self):
        return reverse('rifa_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        # Si es la primera vez que se guarda, establecer tickets_disponibles
        if not self.pk:
            self.tickets_disponibles = self.total_tickets
        super().save(*args, **kwargs)

    def tickets_vendidos(self):
        """Retorna la cantidad de tickets vendidos"""
        return self.total_tickets - self.tickets_disponibles

    def porcentaje_vendido(self):
        """Retorna el porcentaje de tickets vendidos"""
        if self.total_tickets > 0:
            return (self.tickets_vendidos() / self.total_tickets) * 100
        return 0

    def puede_vender_tickets(self):
        """Verifica si se pueden vender más tickets"""
        return (self.estado == 'activa' and 
                self.tickets_disponibles > 0 and 
                timezone.now() < self.fecha_fin)

    def seleccionar_ganador(self):
        """Selecciona un ganador aleatorio entre los tickets vendidos"""
        if self.estado != 'finalizada' and self.tickets_vendidos() > 0:
            tickets = self.tickets.all()
            if tickets.exists():
                ganador_ticket = random.choice(tickets)
                self.ganador = ganador_ticket.usuario
                self.estado = 'finalizada'
                self.save()
                return self.ganador
        return None


# ---------------------
# MODELO DE TICKET UNIFICADO
# ---------------------
class Ticket(models.Model):
    """Modelo unificado para tickets de rifas"""
    # Identificación
    codigo = models.CharField(max_length=20, unique=True, editable=False, null=True, blank=True, verbose_name="Código del Ticket")
    numero = models.PositiveIntegerField(default=1, verbose_name="Número de Ticket")
    
    # Relaciones
    rifa = models.ForeignKey(
        Rifa, 
        on_delete=models.CASCADE, 
        related_name='tickets',
        verbose_name="Rifa",
        null=True,
        blank=True
    )
    usuario = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='tickets_comprados',
        verbose_name="Usuario",
        null=True,
        blank=True
    )
    
    # Información de compra
    fecha_compra = models.DateTimeField(default=timezone.now, verbose_name="Fecha de Compra")
    precio_pagado = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Precio Pagado"
    )
    
    # Estado del ticket
    activo = models.BooleanField(default=True, verbose_name="Ticket Activo")
    
    # Factura asociada
    factura = models.ForeignKey(
        Factura, 
        on_delete=models.CASCADE, 
        related_name='tickets',
        verbose_name="Factura",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['numero']
        unique_together = ['rifa', 'numero']

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = f"TCK-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket {self.numero} - {self.rifa.titulo}"

    def es_ganador(self):
        """Verifica si este ticket es el ganador"""
        return self.rifa.ganador == self.usuario


# ---------------------
# MODELO DE SAN UNIFICADO
# ---------------------
class San(models.Model):
    """Modelo unificado para sanes"""
    FRECUENCIAS_PAGO = [
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
    ]
    
    TIPOS_SAN = [
        ('ahorro', 'Ahorro'),
        ('producto', 'Producto'),
        ('servicio', 'Servicio'),
    ]
    
    ESTADOS_SAN = [
        ('borrador', 'Borrador'),
        ('activo', 'Activo'),
        ('pausado', 'Pausado'),
        ('finalizado', 'Finalizado'),
        ('cancelado', 'Cancelado'),
    ]

    # Información básica
    nombre = models.CharField(max_length=200, blank=True, verbose_name="Nombre del San")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    
    # Configuración financiera
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Precio Total")
    numero_cuotas = models.PositiveIntegerField(default=1, verbose_name="Número de Cuotas")
    precio_cuota = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Precio por Cuota")
    
    # Configuración de participantes
    total_participantes = models.PositiveIntegerField(default=10, verbose_name="Total de Participantes")
    participantes_actuales = models.PositiveIntegerField(default=0, verbose_name="Participantes Actuales")
    
    # Configuración de pagos
    frecuencia_pago = models.CharField(
        max_length=20, 
        choices=FRECUENCIAS_PAGO, 
        default='mensual',
        verbose_name="Frecuencia de Pago"
    )
    
    # Tipo y estado
    tipo = models.CharField(
        max_length=20, 
        choices=TIPOS_SAN, 
        default='ahorro',
        verbose_name="Tipo de San"
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS_SAN, 
        default='borrador',
        verbose_name="Estado"
    )
    
    # Organizador
    organizador = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='sanes_organizados',
        verbose_name="Organizador"
    )
    
    # Fechas
    fecha_inicio = models.DateField(default=date.today, verbose_name="Fecha de Inicio")
    fecha_fin = models.DateField(default=date.today, verbose_name="Fecha de Finalización")
    
    # Imagen
    imagen = models.ImageField(
        upload_to='sanes_images/', 
        blank=True, 
        null=True,
        verbose_name="Imagen del San"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = 'San'
        verbose_name_plural = 'Sanes'
        ordering = ['-created_at']

    def __str__(self):
        return self.nombre
    
    @property
    def comentarios(self):
        """Retorna los comentarios activos del san"""
        return Comment.objects.filter(
            content_type=ContentType.objects.get_for_model(self),
            object_id=self.id,
            activo=True
        )

    def get_absolute_url(self):
        return reverse('san_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        # Calcular precio por cuota si no está establecido
        if not self.precio_cuota and self.numero_cuotas > 0:
            self.precio_cuota = self.precio_total / self.numero_cuotas
        super().save(*args, **kwargs)

    def cupos_disponibles(self):
        """Retorna la cantidad de cupos disponibles"""
        return self.total_participantes - self.participantes_actuales

    def porcentaje_ocupado(self):
        """Retorna el porcentaje de cupos ocupados"""
        if self.total_participantes > 0:
            return (self.participantes_actuales / self.total_participantes) * 100
        return 0

    def puede_agregar_participante(self):
        """Verifica si se puede agregar un nuevo participante"""
        return (self.estado == 'activo' and 
                self.cupos_disponibles() > 0 and 
                date.today() <= self.fecha_fin)

    def agregar_participante(self, usuario):
        """Agrega un nuevo participante al san"""
        if self.puede_agregar_participante():
            participacion = ParticipacionSan.objects.create(
                san=self,
                usuario=usuario
            )
            self.participantes_actuales += 1
            self.save()
            return participacion
        return None


# ---------------------
# MODELO DE PARTICIPACIÓN EN SAN
# ---------------------
class ParticipacionSan(models.Model):
    """Modelo para la participación de usuarios en sanes"""
    # Relaciones
    san = models.ForeignKey(
        San, 
        on_delete=models.CASCADE, 
        related_name='participaciones',
        verbose_name="San"
    )
    usuario = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='participaciones_san',
        verbose_name="Usuario"
    )
    
    # Información de la participación
    fecha_inscripcion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Inscripción")
    orden_cobro = models.PositiveIntegerField(default=1, verbose_name="Orden de Cobro")
    
    # Estado de la participación
    activa = models.BooleanField(default=True, verbose_name="Participación Activa")
    
    # Seguimiento de cuotas
    cuotas_pagadas = models.PositiveIntegerField(default=0, verbose_name="Cuotas Pagadas")
    fecha_ultima_cuota = models.DateField(null=True, blank=True, verbose_name="Fecha de Última Cuota")

    class Meta:
        verbose_name = 'Participación en San'
        verbose_name_plural = 'Participaciones en San'
        ordering = ['orden_cobro']
        unique_together = ['san', 'usuario']

    def __str__(self):
        return f"{self.usuario.get_full_name_or_username()} - {self.san.nombre}"

    def cuotas_pendientes(self):
        """Retorna la cantidad de cuotas pendientes"""
        return self.san.numero_cuotas - self.cuotas_pagadas

    def monto_pendiente(self):
        """Retorna el monto pendiente de pago"""
        return self.cuotas_pendientes() * self.san.precio_cuota

    def proxima_fecha_cuota(self):
        """Calcula la próxima fecha de cuota"""
        if not self.fecha_ultima_cuota:
            return self.san.fecha_inicio
        
        if self.san.frecuencia_pago == 'semanal':
            return self.fecha_ultima_cuota + timedelta(weeks=1)
        elif self.san.frecuencia_pago == 'quincenal':
            return self.fecha_ultima_cuota + timedelta(weeks=2)
        else:  # mensual
            return self.fecha_ultima_cuota + timedelta(days=30)

    def registrar_pago_cuota(self):
        """Registra el pago de una cuota"""
        self.cuotas_pagadas += 1
        self.fecha_ultima_cuota = date.today()
        self.save()
    
    @property
    def total_pagado(self):
        """Retorna el total pagado por el participante"""
        return self.cuotas_pagadas * self.san.precio_cuota
    
    @property
    def porcentaje_completado(self):
        """Retorna el porcentaje de cuotas pagadas"""
        if self.san.numero_cuotas > 0:
            return (self.cuotas_pagadas / self.san.numero_cuotas) * 100
        return 0
    
    @property
    def numero_cupo(self):
        """Retorna el número de cupo asignado"""
        return self.orden_cobro


# ---------------------
# MODELO DE CUPO UNIFICADO
# ---------------------
class Cupo(models.Model):
    """Modelo unificado para cupos de sanes"""
    ESTADOS_CUPO = [
        ('disponible', 'Disponible'),
        ('asignado', 'Asignado'),
        ('pagado', 'Pagado'),
        ('vencido', 'Vencido'),
    ]

    # Relaciones
    san = models.ForeignKey(
        San, 
        on_delete=models.CASCADE, 
        related_name='cupos',
        verbose_name="San"
    )
    participacion = models.ForeignKey(
        ParticipacionSan, 
        on_delete=models.CASCADE, 
        related_name='cupos',
        verbose_name="Participación",
        null=True,
        blank=True
    )
    
    # Información del cupo
    numero_semana = models.PositiveIntegerField(default=1, verbose_name="Número de Semana")
    fecha_vencimiento = models.DateField(
        verbose_name="Fecha de Vencimiento",
        null=True,   # <--- permitimos que inicialmente sea NULL
        blank=True
    )
    
    # Estado y asignación
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS_CUPO, 
        default='disponible',
        verbose_name="Estado"
    )
    asignado = models.BooleanField(default=False, verbose_name="Cupo Asignado")
    
    # Información de pago
    monto_cuota = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Monto de la Cuota",
        default=0.00
    )

    
    def clean(self):
        if self.monto_cuota <= 0:
            raise ValidationError("El monto de la cuota debe ser mayor a 0.")

    fecha_pago = models.DateField(null=True, blank=True, verbose_name="Fecha de Pago")
    
    # Factura asociada
    factura = models.ForeignKey(
        Factura, 
        on_delete=models.CASCADE, 
        related_name='cupos',
        verbose_name="Factura",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Cupo'
        verbose_name_plural = 'Cupos'
        ordering = ['numero_semana']
        unique_together = ['san', 'numero_semana']

    def __str__(self):
        return f"Cupo {self.numero_semana} - {self.san.nombre}"

    def asignar_a_participante(self, participacion):
        if self.estado == 'disponible':
            self.participacion = participacion
            self.asignado = True
            self.estado = 'asignado'
            self.fecha_vencimiento = date.today() + timedelta(days=30)
            self.save()
            return True
        return False


    def registrar_pago(self, factura):
        """Registra el pago del cupo"""
        self.estado = 'pagado'
        self.fecha_pago = date.today()
        self.factura = factura
        self.save()

    def is_vencido(self):
        """Verifica si el cupo está vencido"""
        return date.today() > self.fecha_vencimiento


# ---------------------
# MODELO DE ORDEN UNIFICADO
# ---------------------
class Orden(models.Model):
    """Modelo unificado para órdenes de compra"""
    ESTADOS_ORDEN = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('completada', 'Completada'),
    ]

    # Identificación
    codigo = models.CharField(max_length=20, unique=True, editable=False, null=True, blank=True, verbose_name="Código de Orden")
    
    # Usuario que realiza la orden
    usuario = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='ordenes',
        verbose_name="Usuario"
    )
    
    # Contenido genérico (Rifa o San)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tipo de Contenido")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID del Objeto")
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Información de la orden
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    
    # Montos
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Subtotal")
    impuestos = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Impuestos")
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total")
    
    # Estado
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS_ORDEN, 
        default='pendiente',
        verbose_name="Estado"
    )
    
    # Notas
    notas = models.TextField(blank=True, null=True, verbose_name="Notas")

    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        ordering = ['-fecha_creacion']

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Orden {self.codigo} - {self.usuario.get_full_name_or_username()}"

    def get_tipo_contenido(self):
        """Retorna el tipo de contenido (Rifa o San)"""
        return self.content_type.model_class().__name__

    def confirmar(self):
        """Confirma la orden"""
        self.estado = 'confirmada'
        self.save()

    def cancelar(self):
        """Cancela la orden"""
        self.estado = 'cancelada'
        self.save()

    def completar(self):
        """Marca la orden como completada"""
        self.estado = 'completada'
        self.save()


# ---------------------
# MODELO DE PAGO UNIFICADO
# ---------------------
class Pago(models.Model):
    """Modelo unificado para pagos"""
    ESTADOS_PAGO = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('rechazado', 'Rechazado'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('otro', 'Otro'),
    ]

    # Identificación
    codigo = models.CharField(max_length=20, unique=True, editable=False, null=True, blank=True, verbose_name="Código de Pago")
    
    # Usuario que realiza el pago
    usuario = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='pagos_realizados',
        verbose_name="Usuario"
    )
    
    # Contenido genérico (Rifa, San, o Cupo)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tipo de Contenido")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID del Objeto")
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Información del pago
    fecha_pago = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Pago")
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Monto")
    
    # Estado y método
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS_PAGO, 
        default='pendiente',
        verbose_name="Estado"
    )
    metodo_pago = models.CharField(
        max_length=20, 
        choices=METODOS_PAGO, 
        default='efectivo',
        verbose_name="Método de Pago"
    )
    
    # Comprobante y notas
    comprobante_pago = models.ImageField(
        upload_to='comprobantes/', 
        blank=True, 
        null=True,
        verbose_name="Comprobante de Pago"
    )
    notas = models.TextField(blank=True, null=True, verbose_name="Notas")
    
    # Orden y factura asociadas
    orden = models.ForeignKey(
        Orden, 
        on_delete=models.CASCADE, 
        related_name='pagos',
        verbose_name="Orden",
        null=True,
        blank=True
    )
    factura = models.ForeignKey(
        Factura, 
        on_delete=models.CASCADE, 
        related_name='pagos',
        verbose_name="Factura",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha_pago']

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = f"PAG-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pago {self.codigo} - {self.usuario.get_full_name_or_username()}"

    def get_tipo_contenido(self):
        """Retorna el tipo de contenido"""
        return self.content_type.model_class().__name__

    def confirmar(self):
        """Confirma el pago"""
        self.estado = 'confirmado'
        self.save()

    def rechazar(self):
        """Rechaza el pago"""
        self.estado = 'rechazado'
        self.save()

    def cancelar(self):
        """Cancela el pago"""
        self.estado = 'cancelado'
        self.save()


# ---------------------
# MODELOS DE SOPORTE
# ---------------------
class Comentario(models.Model):
    """Modelo para comentarios en rifas y sanes"""
    # Contenido genérico
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tipo de Contenido")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID del Objeto")
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Usuario que comenta
    usuario = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        verbose_name="Usuario"
    )
    
    # Contenido del comentario
    comentario = models.TextField(blank=True, verbose_name="Comentario")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    # Estado
    activo = models.BooleanField(default=True, verbose_name="Comentario Activo")

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Comentario de {self.usuario.get_full_name_or_username()}"


class Imagen(models.Model):
    """Modelo para imágenes de rifas y sanes"""
    # Contenido genérico
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tipo de Contenido")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID del Objeto")
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Imagen
    imagen = models.ImageField(upload_to='contenido_images/', null=True, blank=True, verbose_name="Imagen")
    titulo = models.CharField(max_length=200, blank=True, null=True, verbose_name="Título")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    # Orden y estado
    orden = models.PositiveIntegerField(default=0, verbose_name="Orden")
    activa = models.BooleanField(default=True, verbose_name="Imagen Activa")
    
    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    class Meta:
        verbose_name = 'Imagen'
        verbose_name_plural = 'Imágenes'
        ordering = ['orden', '-fecha_creacion']

    def __str__(self):
        return f"Imagen {self.titulo or self.id}"


# ---------------------
# FORMULARIOS
# ---------------------
class CambiarFotoPerfilForm(forms.ModelForm):
    """Formulario para cambiar foto de perfil"""
    class Meta:
        model = CustomUser
        fields = ['foto_perfil']

class Notificacion(models.Model):
    """
    Notificaciones enviadas a los usuarios (ej: recordatorios de pagos,
    resultados de rifas, avisos de admin, etc.)
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones"
    )
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.titulo} → {self.usuario}"


class Reporte(models.Model):
    """
    Registro de reportes generados en el sistema.
    Puede almacenar datos agregados o referencias a rifas/sanes.
    """
    TIPO_REPORTE = [
        ('rifa', 'Rifa'),
        ('san', 'San'),
        ('usuario', 'Usuario'),
        ('finanzas', 'Finanzas'),
    ]

    administrador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reportes_generados"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_REPORTE)
    descripcion = models.TextField()
    archivo = models.FileField(upload_to="reportes/", null=True, blank=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_generacion']

    def __str__(self):
        return f"Reporte {self.tipo} ({self.fecha_generacion.date()})"


class HistorialAccion(models.Model):
    """
    Auditoría básica de acciones importantes en el sistema.
    Útil para control administrativo.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="acciones"
    )
    accion = models.CharField(max_length=255)
    detalle = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario} → {self.accion} ({self.fecha})"

class SorteoRifa(models.Model):
    """
    Registro histórico de cada sorteo de una rifa.
    Permite llevar evidencia del proceso y guardar resultados previos.
    """
    rifa = models.ForeignKey("Rifa", on_delete=models.CASCADE, related_name="sorteos")
    fecha_sorteo = models.DateTimeField(auto_now_add=True)
    ticket_ganador = models.ForeignKey(
        "Ticket",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sorteos_ganados"
    )
    evidencia = models.FileField(upload_to="rifas/evidencias/", null=True, blank=True)

    def __str__(self):
        return f"Sorteo de {self.rifa.nombre} - {self.fecha_sorteo.strftime('%d/%m/%Y')}"



class TurnoSan(models.Model):
    """
    Control más estructurado de los turnos en un sane.
    Útil cuando los turnos se asignan de forma aleatoria o cambian con el tiempo.
    """
    san = models.ForeignKey("San", on_delete=models.CASCADE, related_name="turnos")
    participante = models.ForeignKey(
        "ParticipacionSan",
        on_delete=models.CASCADE,
        related_name="turnos"
    )
    numero_turno = models.PositiveIntegerField()
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    cumplido = models.BooleanField(default=False)

    class Meta:
        unique_together = ("san", "numero_turno")
        ordering = ["numero_turno"]

    def __str__(self):
        return f"Turno {self.numero_turno} - {self.participante.usuario.username} en {self.san.nombre}"
class Mensaje(models.Model):
    """
    Mensajería interna simple entre usuarios (ej. soporte o coordinación).
    """
    remitente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mensajes_enviados"
    )
    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mensajes_recibidos"
    )
    asunto = models.CharField(max_length=255)
    contenido = models.TextField()
    leido = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha_envio"]

    def __str__(self):
        return f"De {self.remitente.username} para {self.destinatario.username} - {self.asunto}"

# ---------------------
# MODELO DE COMENTARIOS
# ---------------------
class Comment(models.Model):
    """Comentarios para rifas y sanes"""
    # Usuario que hace el comentario
    usuario = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        verbose_name="Usuario",
        related_name='comentarios'
    )
    
    # Contenido genérico (Rifa o San)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="Tipo de Contenido")
    object_id = models.PositiveIntegerField(verbose_name="ID del Objeto")
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Contenido del comentario
    texto = models.TextField(verbose_name="Comentario")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    # Estado del comentario
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Comentario de {self.usuario.username} en {self.content_object}"
    
    def get_short_text(self):
        """Retorna el texto truncado para mostrar en listas"""
        return self.texto[:100] + "..." if len(self.texto) > 100 else self.texto


# ---------------------
# MODELO DE LOGS DEL SISTEMA
# ---------------------
class SystemLog(models.Model):
    """Logs de acciones del sistema"""
    TIPOS_ACCION = [
        ('crear', 'Crear'),
        ('editar', 'Editar'),
        ('eliminar', 'Eliminar'),
        ('pagar', 'Pagar'),
        ('confirmar', 'Confirmar'),
        ('rechazar', 'Rechazar'),
        ('comentar', 'Comentar'),
        ('unirse', 'Unirse'),
        ('salir', 'Salir'),
        ('login', 'Iniciar Sesión'),
        ('logout', 'Cerrar Sesión'),
        ('registro', 'Registro'),
        ('admin', 'Acción Administrativa'),
    ]
    
    NIVELES = [
        ('info', 'Información'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('success', 'Éxito'),
    ]
    
    # Usuario que realiza la acción
    usuario = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Usuario",
        related_name='logs'
    )
    
    # Información de la acción
    tipo_accion = models.CharField(max_length=20, choices=TIPOS_ACCION, verbose_name="Tipo de Acción")
    nivel = models.CharField(max_length=10, choices=NIVELES, default='info', verbose_name="Nivel")
    descripcion = models.TextField(verbose_name="Descripción")
    
    # Objeto relacionado (opcional)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Tipo de Contenido")
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name="ID del Objeto")
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Información adicional
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="Dirección IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    # Datos adicionales en JSON
    datos_adicionales = models.JSONField(default=dict, blank=True, verbose_name="Datos Adicionales")
    
    class Meta:
        verbose_name = 'Log del Sistema'
        verbose_name_plural = 'Logs del Sistema'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', 'tipo_accion']),
            models.Index(fields=['fecha_creacion']),
            models.Index(fields=['nivel']),
        ]
    
    def __str__(self):
        return f"{self.tipo_accion} - {self.usuario.username if self.usuario else 'Sistema'} - {self.fecha_creacion.strftime('%d/%m/%Y %H:%M')}"
    
    @classmethod
    def log_action(cls, usuario, tipo_accion, descripcion, nivel='info', content_object=None, ip_address=None, user_agent=None, datos_adicionales=None):
        """Método de clase para crear logs fácilmente"""
        return cls.objects.create(
            usuario=usuario,
            tipo_accion=tipo_accion,
            descripcion=descripcion,
            nivel=nivel,
            content_object=content_object,
            ip_address=ip_address,
            user_agent=user_agent,
            datos_adicionales=datos_adicionales or {}
        )