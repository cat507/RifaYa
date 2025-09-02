from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import (
    CustomUser, Rifa, San, ParticipacionSan, Cupo, 
    Factura, PagoSimulado, Comment, SystemLog, NotificacionMejorada,
    Notificacion, Reporte, HistorialAccion, SorteoRifa, TurnoSan, Mensaje
)

# ---------------------
# FORMULARIOS DE AUTENTICACIÓN
# ---------------------
class CustomLoginForm(forms.Form):
    """Formulario personalizado de login"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Correo electrónico'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Contraseña'
        })
    )
    remember = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise ValidationError('Credenciales inválidas. Por favor, verifica tu correo y contraseña.')
            cleaned_data['user'] = user
        return cleaned_data


class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado de registro de usuarios"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Correo electrónico'
        })
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Apellido'
        })
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Número de teléfono (opcional)'
        })
    )
    cedula = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Cédula (opcional)'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'cedula', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar campos de contraseña
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Nombre de usuario'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'placeholder': 'Confirmar contraseña'
        })


# ---------------------
# FORMULARIOS DE RIFAS
# ---------------------
class RifaForm(forms.ModelForm):
    """Formulario para crear/editar rifas"""
    class Meta:
        model = Rifa
        fields = ['titulo', 'descripcion', 'premio', 'precio_ticket', 'total_tickets', 'fecha_fin', 'imagen']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Título de la rifa'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'rows': 4,
                'placeholder': 'Descripción de la rifa'
            }),
            'premio': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Descripción del premio'
            }),
            'precio_ticket': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Precio por ticket'
            }),
            'total_tickets': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'min': '1',
                'placeholder': 'Número total de tickets'
            }),
            'fecha_fin': forms.DateTimeInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'type': 'datetime-local'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'accept': 'image/*'
            })
        }


# ---------------------
# FORMULARIOS DE SANES
# ---------------------
class SanForm(forms.ModelForm):
    """Formulario para crear/editar SANes"""
    class Meta:
        model = San
        fields = ['nombre', 'descripcion', 'precio_total', 'numero_cuotas', 'total_participantes', 'frecuencia_pago', 'tipo', 'fecha_inicio', 'fecha_fin', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Nombre del SAN'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'rows': 4,
                'placeholder': 'Descripción del SAN'
            }),
            'precio_total': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Precio total'
            }),
            'numero_cuotas': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'min': '1',
                'placeholder': 'Número de cuotas'
            }),
            'total_participantes': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'min': '1',
                'placeholder': 'Total de participantes'
            }),
            'frecuencia_pago': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'tipo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'type': 'date'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'type': 'date'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'accept': 'image/*'
            })
        }


# ---------------------
# FORMULARIOS DE PARTICIPACIÓN
# ---------------------
class ParticipacionSanForm(forms.ModelForm):
    """Formulario para participar en un SAN"""
    class Meta:
        model = ParticipacionSan
        fields = []  # No hay campos editables por el usuario


# ---------------------
# FORMULARIOS DE CUPOS
# ---------------------
class CupoForm(forms.ModelForm):
    """Formulario para gestionar cupos de SAN"""
    class Meta:
        model = Cupo
        fields = ['estado', 'monto_cuota', 'fecha_vencimiento']
        widgets = {
            'estado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'monto_cuota': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'min': '0.01',
                'step': '0.01'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'type': 'date'
            })
        }


# ---------------------
# FORMULARIOS DE FACTURAS
# ---------------------
class FacturaForm(forms.ModelForm):
    """Formulario para crear/editar facturas"""
    class Meta:
        model = Factura
        fields = ['monto_total', 'fecha_vencimiento', 'estado_pago', 'metodo_pago', 'comprobante_pago', 'notas']
        widgets = {
            'monto_total': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Monto total'
            }),
            'fecha_vencimiento': forms.DateTimeInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'type': 'datetime-local'
            }),
            'estado_pago': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'metodo_pago': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'comprobante_pago': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'accept': 'image/*,.pdf'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'rows': 3,
                'placeholder': 'Notas adicionales'
            })
        }


# ---------------------
# FORMULARIOS DE PAGOS SIMULADOS
# ---------------------
class PagoSimuladoForm(forms.ModelForm):
    """Formulario para pagos simulados"""
    class Meta:
        model = PagoSimulado
        fields = ['metodo_pago', 'monto', 'moneda']
        widgets = {
            'metodo_pago': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Monto del pago'
            }),
            'moneda': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            })
        }


# ---------------------
# FORMULARIOS DE COMENTARIOS
# ---------------------
class CommentForm(forms.ModelForm):
    """Formulario para crear y editar comentarios"""
    class Meta:
        model = Comment
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'rows': 4,
                'placeholder': 'Escribe tu comentario aquí...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['texto'].label = "Comentario"


class CommentEditForm(forms.ModelForm):
    """Formulario para editar comentarios existentes"""
    class Meta:
        model = Comment
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'rows': 4,
                'placeholder': 'Edita tu comentario aquí...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['texto'].label = "Editar Comentario"


class CommentModerationForm(forms.ModelForm):
    """Formulario para moderar comentarios (solo admin)"""
    class Meta:
        model = Comment
        fields = ['estado', 'motivo_moderacion']
        widgets = {
            'estado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'motivo_moderacion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'rows': 3,
                'placeholder': 'Describe el motivo de la moderación...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['estado'].label = "Estado del Comentario"
        self.fields['motivo_moderacion'].label = "Motivo de Moderación"


# ---------------------
# FORMULARIOS DE PERFIL
# ---------------------
class PerfilForm(forms.ModelForm):
    """Formulario para editar perfil de usuario"""
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'address', 'date_of_birth', 'cedula', 'oficio', 'whatsapp', 'facebook', 'instagram', 'foto_perfil']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'type': 'date'
            }),
            'cedula': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'oficio': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'whatsapp': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'facebook': forms.URLInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'instagram': forms.URLInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'foto_perfil': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'accept': 'image/*'
            })
        }


# ---------------------
# FORMULARIOS DE COMPRA DE TICKETS
# ---------------------
class CompraTicketForm(forms.Form):
    """Formulario para comprar tickets de rifa"""
    cantidad = forms.IntegerField(
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
            'min': '1',
            'max': '10'
        })
    )
    metodo_pago = forms.ChoiceField(
        choices=[
            ('efectivo', 'Efectivo'),
            ('transferencia', 'Transferencia Bancaria'),
            ('paypal', 'PayPal'),
            ('stripe', 'Stripe'),
            ('nequi', 'Nequi'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
        })
    )


# ---------------------
# FORMULARIOS DE INSCRIPCIÓN A SAN
# ---------------------
class InscripcionSanForm(forms.Form):
    """Formulario para inscribirse a un SAN"""
    metodo_pago = forms.ChoiceField(
        choices=[
            ('efectivo', 'Efectivo'),
            ('transferencia', 'Transferencia Bancaria'),
            ('paypal', 'PayPal'),
            ('stripe', 'Stripe'),
            ('nequi', 'Nequi'),
        ],
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
        })
    )
    acepto_terminos = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded'
        })
    )


# ---------------------
# FORMULARIOS DE NOTIFICACIONES
# ---------------------
class NotificacionAdminForm(forms.ModelForm):
    """Formulario para que el admin envíe notificaciones a usuarios"""
    class Meta:
        model = NotificacionMejorada
        fields = ['usuario', 'tipo', 'titulo', 'mensaje', 'prioridad', 'canal']
        widgets = {
            'usuario': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'tipo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Título de la notificación...'
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'rows': 4,
                'placeholder': 'Mensaje de la notificación...'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'canal': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo usuarios activos
        self.fields['usuario'].queryset = CustomUser.objects.filter(is_active=True)
        self.fields['usuario'].label = "Usuario Destinatario"
        self.fields['tipo'].label = "Tipo de Notificación"
        self.fields['titulo'].label = "Título"
        self.fields['mensaje'].label = "Mensaje"
        self.fields['prioridad'].label = "Prioridad"
        self.fields['canal'].label = "Canal de Envío"


class NotificacionMasivaForm(forms.ModelForm):
    """Formulario para envío masivo de notificaciones"""
    usuarios = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'space-y-2'
        }),
        required=True,
        label="Seleccionar Usuarios"
    )
    
    class Meta:
        model = NotificacionMejorada
        fields = ['tipo', 'titulo', 'mensaje', 'prioridad', 'canal']
        widgets = {
            'tipo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'titulo': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'placeholder': 'Título de la notificación...'
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
                'rows': 4,
                'placeholder': 'Mensaje de la notificación...'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            }),
            'canal': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo'].label = "Tipo de Notificación"
        self.fields['titulo'].label = "Título"
        self.fields['mensaje'].label = "Mensaje"
        self.fields['prioridad'].label = "Prioridad"
        self.fields['canal'].label = "Canal de Envío"
        
        # Agrupar usuarios por tipo para facilitar selección
        self.fields['usuarios'].queryset = CustomUser.objects.filter(is_active=True).order_by('username')
