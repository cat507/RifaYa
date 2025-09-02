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
from django.core.validators import MinValueValidator, MaxValueValidator


# ---------------------
# MODELO DE USUARIO UNIFICADO MEJORADO
# ---------------------
class CustomUser(AbstractUser):
    """Usuario personalizado con roles, permisos y sistema de reputación"""
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Número de Teléfono")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")
    cedula = models.CharField(max_length=20, blank=True, null=True, verbose_name="Cédula")
    oficio = models.CharField(max_length=100, blank=True, null=True, verbose_name="Oficio")
    
    # Roles mejorados
    ROLES_CHOICES = [
        ('usuario', 'Usuario Participante'), 
        ('organizador', 'Organizador'),
        ('administrador', 'Administrador del Sistema')
    ]
    rol = models.CharField(
        max_length=20, 
        choices=ROLES_CHOICES, 
        default='usuario',
        verbose_name="Rol"
    )
    
    # Sistema de reputación
    puntuacion_reputacion = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Puntuación de Reputación"
    )
    nivel_reputacion = models.CharField(
        max_length=20,
        choices=[
            ('nuevo', 'Nuevo'),
            ('confiable', 'Confiable'),
            ('excelente', 'Excelente'),
            ('premium', 'Premium')
        ],
        default='nuevo',
        verbose_name="Nivel de Reputación"
    )
    
    # Verificación de identidad
    verificado = models.BooleanField(default=False, verbose_name="Usuario Verificado")
    fecha_verificacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Verificación")
    documento_identidad = models.FileField(
        upload_to='documentos_identidad/',
        null=True,
        blank=True,
        verbose_name="Documento de Identidad"
    )
    
    # Configuración de seguridad
    dos_fa_habilitado = models.BooleanField(default=False, verbose_name="2FA Habilitado")
    ultimo_login = models.DateTimeField(null=True, blank=True, verbose_name="Último Login")
    intentos_login_fallidos = models.PositiveIntegerField(default=0, verbose_name="Intentos de Login Fallidos")
    bloqueado_hasta = models.DateTimeField(null=True, blank=True, verbose_name="Bloqueado Hasta")
    
    # Información de contacto adicional
    whatsapp = models.CharField(max_length=15, blank=True, null=True, verbose_name="WhatsApp")
    facebook = models.URLField(blank=True, null=True, verbose_name="Facebook")
    instagram = models.URLField(blank=True, null=True, verbose_name="Instagram")
    
    # Foto de perfil
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
        """Verifica si el usuario es administrador del sistema"""
        return self.rol == 'administrador'
    
    def is_organizador(self):
        """Verifica si el usuario es organizador"""
        return self.rol == 'organizador'
    
    def is_participante(self):
        """Verifica si el usuario es participante"""
        return self.rol == 'usuario'

    def get_full_name_or_username(self):
        """Retorna el nombre completo o username como fallback"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def actualizar_reputacion(self, puntos):
        """Actualiza la puntuación de reputación del usuario"""
        nueva_puntuacion = max(0, min(100, self.puntuacion_reputacion + puntos))
        self.puntuacion_reputacion = nueva_puntuacion
        
        # Actualizar nivel de reputación
        if nueva_puntuacion >= 90:
            self.nivel_reputacion = 'premium'
        elif nueva_puntuacion >= 75:
            self.nivel_reputacion = 'excelente'
        elif nueva_puntuacion >= 50:
            self.nivel_reputacion = 'confiable'
        else:
            self.nivel_reputacion = 'nuevo'
        
        self.save()
    
    def puede_participar(self):
        """Verifica si el usuario puede participar en actividades"""
        return (
            self.is_active and 
            not self.bloqueado_hasta or 
            timezone.now() > self.bloqueado_hasta
        )
    
    def registrar_intento_login_fallido(self):
        """Registra un intento de login fallido"""
        self.intentos_login_fallidos += 1
        if self.intentos_login_fallidos >= 5:
            # Bloquear por 30 minutos
            self.bloqueado_hasta = timezone.now() + timedelta(minutes=30)
        self.save()
    
    def reset_intentos_login(self):
        """Resetea los intentos de login fallidos"""
        self.intentos_login_fallidos = 0
        self.bloqueado_hasta = None
        self.save()
    
    def verificar_identidad(self):
        """Marca al usuario como verificado"""
        self.verificado = True
        self.fecha_verificacion = timezone.now()
        self.save()
    
    def get_estadisticas_participacion(self):
        """Retorna estadísticas de participación del usuario"""
        from django.db.models import Count, Sum
        
        # Estadísticas de rifas
        rifas_participadas = self.tickets_comprados.values('rifa').distinct().count()
        tickets_comprados = self.tickets_comprados.count()
        rifas_ganadas = self.rifas_ganadas.count()
        
        # Estadísticas de sanes
        sanes_participados = self.participaciones_san.values('san').distinct().count()
        cuotas_pagadas = self.participaciones_san.aggregate(
            total=Sum('cuotas_pagadas')
        )['total'] or 0
        
        return {
            'rifas_participadas': rifas_participadas,
            'tickets_comprados': tickets_comprados,
            'rifas_ganadas': rifas_ganadas,
            'sanes_participados': sanes_participados,
            'cuotas_pagadas': cuotas_pagadas,
        }


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
    
    # Campos para compatibilidad con código existente
    concepto = models.CharField(max_length=255, blank=True, null=True, verbose_name="Concepto")
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Monto")
    tipo = models.CharField(max_length=20, choices=TIPOS_CHOICES, default='otro', verbose_name="Tipo")
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='pendiente', verbose_name="Estado")
    
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
    
    # Campos adicionales para compatibilidad
    fecha_pago = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Pago")
    rifa = models.ForeignKey('Rifa', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Rifa")
    san = models.ForeignKey('San', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="San")
    archivo = models.FileField(upload_to='facturas/', null=True, blank=True, verbose_name="Archivo")

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha_emision']

    def save(self, *args, **kwargs):
        if not self.codigo:
            # Generar código único basado en el tipo de contenido
            if self.content_type and self.content_type.model == 'rifa':
                prefijo = 'RIFA'
            elif self.content_type and self.content_type.model == 'san':
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
        if self.content_type:
            return self.content_type.model_class().__name__
        return "General"

    def get_monto_pendiente(self):
        """Calcula el monto pendiente de pago"""
        return self.monto_total - self.monto_pagado

    def is_pagada(self):
        """Verifica si la factura está completamente pagada"""
        return self.estado_pago == 'confirmado' and self.monto_pagado >= self.monto_total

    def is_vencida(self):
        """Verifica si la factura está vencida"""
        return timezone.now() > self.fecha_vencimiento
    
    # Métodos para compatibilidad con código existente
    @property
    def id_unico(self):
        """Alias para el código de la factura"""
        return self.codigo
    
    def get_estado_display(self):
        """Retorna el estado para compatibilidad"""
        return self.get_estado_pago_display()

    def confirmar_pago(self, monto=None):
        """Confirma el pago de la factura"""
        if monto:
            self.monto_pagado = monto
        self.estado_pago = 'confirmado'
        self.fecha_pago = timezone.now()
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
        
        # Si no se especifica número o es el valor por defecto, asignar automáticamente
        if not self.numero or self.numero == 1:
            if self.rifa:
                # Encontrar el siguiente número disponible
                numeros_ocupados = set(self.rifa.tickets.values_list('numero', flat=True))
                if self.pk:  # Si es una actualización, excluir el ticket actual
                    numeros_ocupados.discard(self.numero)
                
                siguiente_numero = 1
                while siguiente_numero in numeros_ocupados:
                    siguiente_numero += 1
                
                self.numero = siguiente_numero
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ticket {self.numero} - {self.rifa.titulo if self.rifa else 'Sin Rifa'}"

    def es_ganador(self):
        """Verifica si este ticket es el ganador"""
        return self.rifa and self.rifa.ganador == self.usuario


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
        null=True,
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
# MODELO DE COMENTARIOS
# ---------------------
class Comment(models.Model):
    """Comentarios para rifas y sanes con sistema de auditoría y moderación"""
    ESTADOS_COMENTARIO = [
        ('activo', 'Activo'),
        ('moderado', 'Moderado'),
        ('eliminado', 'Eliminado'),
        ('oculto', 'Oculto'),
    ]
    
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
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS_COMENTARIO, 
        default='activo',
        verbose_name="Estado"
    )
    
    # Campos de auditoría
    fecha_moderacion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Moderación")
    moderado_por = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='comentarios_moderados',
        verbose_name="Moderado Por"
    )
    motivo_moderacion = models.TextField(blank=True, null=True, verbose_name="Motivo de Moderación")
    
    # Campos de edición
    editado = models.BooleanField(default=False, verbose_name="Editado")
    fecha_edicion = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Edición")
    texto_original = models.TextField(blank=True, null=True, verbose_name="Texto Original")
    
    # Sistema de votos
    votos_positivos = models.PositiveIntegerField(default=0, verbose_name="Votos Positivos")
    votos_negativos = models.PositiveIntegerField(default=0, verbose_name="Votos Negativos")
    
    # Respuestas a comentarios
    comentario_padre = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='respuestas',
        verbose_name="Comentario Padre"
    )
    
    # Campos para compatibilidad
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['usuario', 'estado']),
            models.Index(fields=['fecha_creacion']),
        ]

    def __str__(self):
        return f"Comentario de {self.usuario.username} en {self.content_object}"
    
    def save(self, *args, **kwargs):
        # Si es una edición, guardar el texto original
        if self.pk and self.editado and not self.texto_original:
            try:
                original = Comment.objects.get(pk=self.pk)
                self.texto_original = original.texto
            except Comment.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
    
    def get_short_text(self):
        """Retorna el texto truncado para mostrar en listas"""
        return self.texto[:100] + "..." if len(self.texto) > 100 else self.texto
    
    def moderar(self, moderador, motivo, nuevo_estado='moderado'):
        """Modera el comentario"""
        self.estado = nuevo_estado
        self.moderado_por = moderador
        self.motivo_moderacion = motivo
        self.fecha_moderacion = timezone.now()
        self.save()
        
        # Crear log del sistema
        SystemLog.log_action(
            usuario=moderador,
            tipo_accion='moderar_comentario',
            descripcion=f'Comentario moderado: {motivo}',
            nivel='warning',
            content_object=self,
            datos_adicionales={
                'comentario_id': self.id,
                'estado_anterior': 'activo',
                'estado_nuevo': nuevo_estado,
                'motivo': motivo
            }
        )
    
    def eliminar(self, moderador, motivo="Eliminado por moderador"):
        """Elimina el comentario"""
        self.estado = 'eliminado'
        self.moderado_por = moderador
        self.motivo_moderacion = motivo
        self.fecha_moderacion = timezone.now()
        self.save()
        
        # Crear log del sistema
        SystemLog.log_action(
            usuario=moderador,
            tipo_accion='eliminar_comentario',
            descripcion=f'Comentario eliminado: {motivo}',
            nivel='warning',
            content_object=self,
            datos_adicionales={
                'comentario_id': self.id,
                'motivo': motivo
            }
        )
    
    def editar(self, nuevo_texto, usuario):
        """Edita el comentario"""
        if self.usuario == usuario or usuario.is_staff:
            self.texto_original = self.texto
            self.texto = nuevo_texto
            self.editado = True
            self.fecha_edicion = timezone.now()
            self.save()
            
            # Crear log del sistema
            SystemLog.log_action(
                usuario=usuario,
                tipo_accion='editar_comentario',
                descripcion=f'Comentario editado',
                nivel='info',
                content_object=self
            )
            
            return True
        return False
    
    def votar(self, usuario, voto_positivo=True):
        """Vota por el comentario"""
        if self.usuario != usuario:  # No puede votar por su propio comentario
            if voto_positivo:
                self.votos_positivos += 1
            else:
                self.votos_negativos += 1
            self.save()
            
            # Crear log del sistema
            SystemLog.log_action(
                usuario=usuario,
                tipo_accion='votar_comentario',
                descripcion=f'Voto {"positivo" if voto_positivo else "negativo"} en comentario',
                nivel='info',
                content_object=self
            )
            
            return True
        return False
    
    @property
    def puntuacion_total(self):
        """Retorna la puntuación total del comentario"""
        return self.votos_positivos - self.votos_negativos
    
    @property
    def es_respuesta(self):
        """Verifica si es una respuesta a otro comentario"""
        return self.comentario_padre is not None
    
    @property
    def respuestas_count(self):
        """Retorna el número de respuestas"""
        return self.respuestas.filter(estado='activo').count()
    
    def puede_editar(self, usuario):
        """Verifica si el usuario puede editar el comentario"""
        return (self.usuario == usuario and 
                self.estado == 'activo' and 
                not self.editado)
    
    def puede_eliminar(self, usuario):
        """Verifica si el usuario puede eliminar el comentario"""
        return (self.usuario == usuario or 
                usuario.is_staff or 
                usuario.is_superuser)


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


# ---------------------
# MODELO DE PAGOS SIMULADOS
# ---------------------
class PagoSimulado(models.Model):
    """Modelo para simular pagos con diferentes métodos de pago"""
    METODOS_PAGO_SIMULADOS = [
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('nequi', 'Nequi'),
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
    ]
    
    ESTADOS_SIMULACION = [
        ('pendiente', 'Pendiente de Procesamiento'),
        ('procesando', 'Procesando'),
        ('exitoso', 'Exitoso'),
        ('fallido', 'Fallido'),
        ('cancelado', 'Cancelado'),
    ]
    
    # Identificación
    codigo_transaccion = models.CharField(max_length=50, unique=True, editable=False, verbose_name="Código de Transacción")
    
    # Usuario y factura
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='pagos_simulados')
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='pagos_simulados')
    
    # Información del pago
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO_SIMULADOS, verbose_name="Método de Pago")
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Monto")
    moneda = models.CharField(max_length=3, default='USD', verbose_name="Moneda")
    
    # Estado de la simulación
    estado = models.CharField(max_length=20, choices=ESTADOS_SIMULACION, default='pendiente', verbose_name="Estado")
    
    # Información de la transacción simulada
    referencia_externa = models.CharField(max_length=100, blank=True, null=True, verbose_name="Referencia Externa")
    fecha_procesamiento = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Procesamiento")
    
    # Detalles de la simulación
    tiempo_procesamiento = models.PositiveIntegerField(default=0, verbose_name="Tiempo de Procesamiento (segundos)")
    intentos = models.PositiveIntegerField(default=1, verbose_name="Número de Intentos")
    
    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    class Meta:
        verbose_name = 'Pago Simulado'
        verbose_name_plural = 'Pagos Simulados'
        ordering = ['-fecha_creacion']

    def save(self, *args, **kwargs):
        if not self.codigo_transaccion:
            self.codigo_transaccion = f"SIM-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pago Simulado {self.codigo_transaccion} - {self.usuario.username}"
    
    def procesar_pago(self):
        """Simula el procesamiento del pago"""
        import time
        import random
        
        self.estado = 'procesando'
        self.save()

        # Simular tiempo de procesamiento (1-5 segundos)
        tiempo_procesamiento = random.randint(1, 5)
        time.sleep(tiempo_procesamiento)
        
        # Simular éxito o fallo (90% éxito)
        if random.random() < 0.9:
            self.estado = 'exitoso'
            self.fecha_procesamiento = timezone.now()
            self.tiempo_procesamiento = tiempo_procesamiento
            
            # Actualizar la factura
            self.factura.estado_pago = 'confirmado'
            self.factura.monto_pagado = self.monto
            self.factura.fecha_pago = timezone.now()
            self.factura.save()
            
            # Crear log del sistema
            SystemLog.log_action(
                usuario=self.usuario,
                tipo_accion='pagar',
                descripcion=f'Pago simulado exitoso de {self.monto} {self.moneda}',
                nivel='success',
                content_object=self.factura
            )
        else:
            self.estado = 'fallido'
            self.tiempo_procesamiento = tiempo_procesamiento
            
            # Crear log del sistema
            SystemLog.log_action(
                usuario=self.usuario,
                tipo_accion='pagar',
                descripcion=f'Pago simulado fallido de {self.monto} {self.moneda}',
                nivel='error',
                content_object=self.factura
            )
        
        self.save()
        return self.estado == 'exitoso'
    
    def reintentar(self):
        """Reintenta el procesamiento del pago"""
        if self.estado in ['fallido', 'cancelado']:
            self.intentos += 1
            self.estado = 'pendiente'
            self.save()
            return self.procesar_pago()
        return False


# ---------------------
# MODELO DE NOTIFICACIONES MEJORADO
# ---------------------
class NotificacionMejorada(models.Model):
    """Sistema de notificaciones mejorado con diferentes tipos y canales"""
    TIPOS_NOTIFICACION = [
        ('pago', 'Pago'),
        ('rifa', 'Rifa'),
        ('san', 'San'),
        ('sistema', 'Sistema'),
        ('admin', 'Administrativa'),
        ('recordatorio', 'Recordatorio'),
    ]
    
    CANALES = [
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('push', 'Notificación Push'),
        ('interno', 'Interno'),
    ]
    
    PRIORIDADES = [
        ('baja', 'Baja'),
        ('normal', 'Normal'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    # Usuario destinatario
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notificaciones_mejoradas')
    
    # Contenido de la notificación
    tipo = models.CharField(max_length=20, choices=TIPOS_NOTIFICACION, verbose_name="Tipo")
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensaje = models.TextField(verbose_name="Mensaje")
    
    # Configuración
    canal = models.CharField(max_length=20, choices=CANALES, default='interno', verbose_name="Canal")
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default='normal', verbose_name="Prioridad")
    
    # Estado y seguimiento
    leido = models.BooleanField(default=False, verbose_name="Leído")
    enviado = models.BooleanField(default=False, verbose_name="Enviado")
    fecha_envio = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Envío")
    
    # Objeto relacionado (opcional)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_lectura = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Lectura")

    class Meta:
        verbose_name = 'Notificación Mejorada'
        verbose_name_plural = 'Notificaciones Mejoradas'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', 'leido']),
            models.Index(fields=['tipo', 'canal']),
            models.Index(fields=['prioridad']),
        ]

    def __str__(self):
        return f"{self.tipo} - {self.usuario.username}: {self.titulo}"
    
    def marcar_leida(self):
        """Marca la notificación como leída"""
        self.leido = True
        self.fecha_lectura = timezone.now()
        self.save()
    
    def enviar_notificacion(self):
        """Simula el envío de la notificación por el canal especificado"""
        if not self.enviado:
            self.enviado = True
            self.fecha_envio = timezone.now()
            self.save()
            
            # Simular envío según el canal
            if self.canal == 'email':
                self._simular_envio_email()
            elif self.canal == 'whatsapp':
                self._simular_envio_whatsapp()
            elif self.canal == 'sms':
                self._simular_envio_sms()
            
            # Crear log del sistema
            SystemLog.log_action(
                usuario=self.usuario,
                tipo_accion='notificar',
                descripcion=f'Notificación enviada por {self.canal}: {self.titulo}',
                nivel='info',
                content_object=self.content_object
            )
    
    def _simular_envio_email(self):
        """Simula el envío de email"""
        # Aquí se implementaría la lógica real de envío de email
        pass
    
    def _simular_envio_whatsapp(self):
        """Simula el envío de WhatsApp"""
        # Aquí se implementaría la lógica real de envío de WhatsApp
        pass
    
    def _simular_envio_sms(self):
        """Simula el envío de SMS"""
        # Aquí se implementaría la lógica real de envío de SMS
        pass


# ---------------------
# MODELOS DE SOPORTE ADICIONALES
# ---------------------
class Notificacion(models.Model):
    """Notificaciones básicas del sistema"""
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
    """Registro de reportes generados en el sistema"""
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
    """Auditoría básica de acciones importantes en el sistema"""
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
    """Registro histórico de cada sorteo de una rifa"""
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
        return f"Sorteo de {self.rifa.titulo} - {self.fecha_sorteo.strftime('%d/%m/%Y')}"


class TurnoSan(models.Model):
    """Control de turnos en un san con validación de pagos previos"""
    ESTADOS_TURNO = [
        ('pendiente', 'Pendiente'),
        ('activo', 'Activo'),
        ('cumplido', 'Cumplido'),
        ('cancelado', 'Cancelado'),
    ]
    
    san = models.ForeignKey("San", on_delete=models.CASCADE, related_name="turnos")
    participante = models.ForeignKey(
        "ParticipacionSan",
        on_delete=models.CASCADE,
        related_name="turnos"
    )
    numero_turno = models.PositiveIntegerField(verbose_name="Número de Turno")
    fecha_asignacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Asignación")
    fecha_vencimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Vencimiento")
    fecha_cumplimiento = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Cumplimiento")
    
    # Estado del turno
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS_TURNO, 
        default='pendiente',
        verbose_name="Estado del Turno"
    )
    
    # Monto del turno
    monto_turno = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Monto del Turno"
    )
    
    # Validación de pagos previos
    pagos_previos_validados = models.BooleanField(
        default=False, 
        verbose_name="Pagos Previos Validados"
    )
    
    # Notas del turno
    notas = models.TextField(blank=True, null=True, verbose_name="Notas del Turno")
    
    # Campo de compatibilidad
    cumplido = models.BooleanField(default=False, verbose_name="Cumplido")

    class Meta:
        unique_together = ("san", "numero_turno")
        ordering = ["numero_turno"]
        verbose_name = 'Turno de San'
        verbose_name_plural = 'Turnos de San'

    def __str__(self):
        return f"Turno {self.numero_turno} - {self.participante.usuario.username} en {self.san.nombre}"
    
    def save(self, *args, **kwargs):
        # Calcular monto del turno si no está establecido
        if not self.monto_turno:
            self.monto_turno = self.san.precio_cuota
        
        # Establecer fecha de vencimiento si no está establecida
        if not self.fecha_vencimiento:
            if self.san.frecuencia_pago == 'semanal':
                self.fecha_vencimiento = date.today() + timedelta(weeks=self.numero_turno)
            elif self.san.frecuencia_pago == 'quincenal':
                self.fecha_vencimiento = date.today() + timedelta(weeks=self.numero_turno * 2)
            else:  # mensual
                self.fecha_vencimiento = date.today() + timedelta(days=self.numero_turno * 30)
        
        # Sincronizar con el campo de compatibilidad
        if self.estado == 'cumplido':
            self.cumplido = True
        
        super().save(*args, **kwargs)
    
    def puede_activarse(self):
        """Verifica si el turno puede activarse (todos los pagos previos validados)"""
        if self.numero_turno == 1:
            return True  # El primer turno siempre puede activarse
        
        # Verificar que todos los turnos previos estén cumplidos
        turnos_previos = TurnoSan.objects.filter(
            san=self.san,
            numero_turno__lt=self.numero_turno
        ).order_by('numero_turno')
        
        for turno_previo in turnos_previos:
            if turno_previo.estado != 'cumplido':
                return False
        
        return True
    
    def activar_turno(self):
        """Activa el turno si se cumplen las condiciones"""
        if self.puede_activarse():
            self.estado = 'activo'
            self.pagos_previos_validados = True
            self.save()
            
            # Crear log del sistema
            SystemLog.log_action(
                usuario=self.participante.usuario,
                tipo_accion='activar_turno',
                descripcion=f'Turno {self.numero_turno} activado para {self.san.nombre}',
                nivel='success',
                content_object=self.san,
                datos_adicionales={
                    'numero_turno': self.numero_turno,
                    'participante': self.participante.usuario.username
                }
            )
            
            return True
        return False
    
    def cumplir_turno(self):
        """Marca el turno como cumplido"""
        if self.estado == 'activo':
            self.estado = 'cumplido'
            self.cumplido = True
            self.fecha_cumplimiento = timezone.now()
            self.save()
            
            # Crear log del sistema
            SystemLog.log_action(
                usuario=self.participante.usuario,
                tipo_accion='cumplir_turno',
                descripcion=f'Turno {self.numero_turno} cumplido para {self.san.nombre}',
                nivel='success',
                content_object=self.san,
                datos_adicionales={
                    'numero_turno': self.numero_turno,
                    'monto': str(self.monto_turno)
                }
            )
            
            return True
        return False
    
    def is_vencido(self):
        """Verifica si el turno está vencido"""
        return date.today() > self.fecha_vencimiento if self.fecha_vencimiento else False
    
    def get_proximo_turno(self):
        """Retorna el próximo turno del SAN"""
        try:
            return TurnoSan.objects.get(
                san=self.san,
                numero_turno=self.numero_turno + 1
            )
        except TurnoSan.DoesNotExist:
            return None
    
    def get_turno_anterior(self):
        """Retorna el turno anterior del SAN"""
        if self.numero_turno > 1:
            try:
                return TurnoSan.objects.get(
                    san=self.san,
                    numero_turno=self.numero_turno - 1
                )
            except TurnoSan.DoesNotExist:
                return None
        return None


class Mensaje(models.Model):
    """Mensajería interna entre usuarios"""
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
# FORMULARIOS
# ---------------------
class CambiarFotoPerfilForm(forms.ModelForm):
    """Formulario para cambiar foto de perfil"""
    class Meta:
        model = CustomUser
        fields = ['foto_perfil']
