# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import (
    CustomUser, Rifa, San, ParticipacionSan, Cupo, 
    Factura, Pago, Orden, Comentario, Imagen
)

from allauth.account.forms import LoginForm

# ---------------------
# FORMULARIOS DE AUTENTICACIÓN
# ---------------------

class CustomLoginForm(LoginForm):
    """Formulario de login con estilos personalizados"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Campo login
        self.fields["login"].label = "Correo electrónico o usuario"
        self.fields["login"].widget = forms.TextInput(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md "
                         "focus:outline-none focus:ring-2 focus:ring-blue-500 "
                         "focus:border-transparent",
                "placeholder": "Ingresa tu correo o usuario",
            }
        )

        # Campo password
        if "password" in self.fields:
            self.fields["password"].label = "Contraseña"
            self.fields["password"].widget = forms.PasswordInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md "
                             "focus:outline-none focus:ring-2 focus:ring-blue-500 "
                             "focus:border-transparent",
                    "placeholder": "Ingresa tu contraseña",
                }
            )

        # Campo remember
        if "remember" in self.fields:
            self.fields["remember"].label = "Recordarme"

<<<<<<< HEAD
    def clean(self):
        cleaned_data = super().clean()
        # Asegurar que el request esté disponible
        if hasattr(self, 'request') and self.request is None:
            # Si no hay request, crear uno básico
            from django.test import RequestFactory
            factory = RequestFactory()
            self.request = factory.get('/')
        return cleaned_data

=======
>>>>>>> 61950c8 (Corrección de error y estado estable)
class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado de registro de usuarios"""
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        label="Nombre",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Ingresa tu nombre'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        label="Apellido",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Ingresa tu apellido'
        })
    )
    email = forms.EmailField(
        required=True, 
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Ingresa tu correo electrónico'
        })
    )
    cedula = forms.CharField(
        max_length=20, 
        required=True, 
        label="Cédula",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Ingresa tu número de cédula'
        })
    )
    oficio = forms.CharField(
        max_length=100, 
        required=True, 
        label="Oficio",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Ingresa tu oficio o profesión'
        })
    )
    phone_number = forms.CharField(
        max_length=15, 
        required=True, 
        label="Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Ingresa tu número de teléfono'
        })
    )
    address = forms.CharField(
        max_length=255, 
        required=False, 
        label="Dirección",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Ingresa tu dirección (opcional)'
        })
    )
    date_of_birth = forms.DateField(
        required=False, 
        label="Fecha de Nacimiento",
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'type': 'date'
        })
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 'email', 
            'password1', 'password2', 'cedula', 'oficio', 
            'phone_number', 'address', 'date_of_birth'
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if CustomUser.objects.filter(cedula=cedula).exists():
            raise forms.ValidationError('Esta cédula ya está registrada.')
        return cedula

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.cedula = self.cleaned_data['cedula']
        user.oficio = self.cleaned_data['oficio']
        user.phone_number = self.cleaned_data['phone_number']
        user.address = self.cleaned_data['address']
        user.date_of_birth = self.cleaned_data['date_of_birth']
        
        if commit:
            user.save()
        return user

class CambiarFotoPerfilForm(forms.ModelForm):
    """Formulario para cambiar foto de perfil"""
    class Meta:
        model = CustomUser
        fields = ['foto_perfil']
        widgets = {
            'foto_perfil': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            })
        }

class PerfilForm(forms.ModelForm):
    """Formulario para editar perfil de usuario"""
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 'date_of_birth', 'cedula', 'oficio', 'foto_perfil']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nombre de usuario'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Correo electrónico'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Apellido'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Número de teléfono'
            }),
            'address': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Dirección'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'cedula': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Número de cédula'
            }),
            'oficio': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Oficio o profesión'
            }),
            'foto_perfil': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            })
        }

# ---------------------
# FORMULARIOS DE RIFAS
# ---------------------
class RifaForm(forms.ModelForm):
    """Formulario para crear/editar rifas"""
<<<<<<< HEAD
    # Campo adicional opcional para cálculos (no se guarda en el modelo)
    valor_premio_monetario = forms.DecimalField(
        required=False,
        min_value=0,
        label="Valor del premio (monetario, opcional)",
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Valor monetario del premio (si aplica)',
            'min': '0',
            'step': '0.01'
        })
    )
=======
>>>>>>> 61950c8 (Corrección de error y estado estable)
    class Meta:
        model = Rifa
        fields = [
            'titulo', 'descripcion', 'premio', 'precio_ticket', 
            'total_tickets', 'fecha_fin', 'estado', 'imagen'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ingresa el título de la rifa'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Describe el premio en detalle',
                'rows': 4
            }),
            'premio': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ingresa el nombre del premio'
            }),
            'precio_ticket': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Precio por ticket',
                'min': '0.01',
                'step': '0.01'
            }),
            'total_tickets': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Total de tickets disponibles',
                'min': '1'
            }),
            'fecha_fin': forms.DateTimeInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'datetime-local'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            })
        }

# ---------------------
# FORMULARIOS DE SANES
# ---------------------
class SanForm(forms.ModelForm):
    """Formulario para crear/editar sanes"""
    class Meta:
        model = San
        fields = [
            'nombre', 'descripcion', 'precio_total', 'numero_cuotas',
            'total_participantes', 'frecuencia_pago', 'tipo', 'estado', 
            'fecha_inicio', 'fecha_fin', 'imagen'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ingresa el nombre del san'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Describe el san en detalle',
                'rows': 4
            }),
            'precio_total': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Precio total del san',
                'min': '0.01',
                'step': '0.01'
            }),
            'numero_cuotas': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Número de cuotas',
                'min': '1'
            }),
            'total_participantes': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Total de participantes',
                'min': '1'
            }),
            'frecuencia_pago': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'tipo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'fecha_inicio': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            })
        }

# ---------------------
# FORMULARIOS DE PARTICIPACIÓN
# ---------------------
class ParticipacionSanForm(forms.ModelForm):
    """Formulario para participación en sanes"""
    class Meta:
        model = ParticipacionSan
        fields = ['orden_cobro']
        widgets = {
            'orden_cobro': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '1'
            })
        }

# ---------------------
# FORMULARIOS DE CUPOS
# ---------------------
class CupoForm(forms.ModelForm):
    """Formulario para cupos de sanes"""
    class Meta:
        model = Cupo
        fields = ['numero_semana', 'monto_cuota', 'fecha_vencimiento', 'estado']
        widgets = {
            'numero_semana': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '1'
            }),
            'monto_cuota': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '0.01',
                'step': '0.01'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            })
        }

# ---------------------
# FORMULARIOS DE FACTURAS
# ---------------------
class FacturaForm(forms.ModelForm):
    """Formulario para facturas"""
    class Meta:
        model = Factura
<<<<<<< HEAD
        fields = ['monto_total', 'fecha_vencimiento', 'estado_pago', 'metodo_pago', 'comprobante_pago', 'notas']
        widgets = {
=======
        fields = ['concepto', 'monto', 'tipo', 'estado', 'monto_total', 'estado_pago', 'metodo_pago', 'fecha_vencimiento', 'notas']
        widgets = {
            'concepto': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Concepto de la factura'
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Monto'
            }),
            'tipo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
>>>>>>> 61950c8 (Corrección de error y estado estable)
            'monto_total': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Monto total'
            }),
<<<<<<< HEAD
            'fecha_vencimiento': forms.DateTimeInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'datetime-local'
            }),
=======
>>>>>>> 61950c8 (Corrección de error y estado estable)
            'estado_pago': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'metodo_pago': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
<<<<<<< HEAD
            'comprobante_pago': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*,.pdf'
=======
            'fecha_vencimiento': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
>>>>>>> 61950c8 (Corrección de error y estado estable)
            }),
            'notas': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Notas adicionales'
            })
        }

# ---------------------
# FORMULARIOS DE COMPROBANTES DE PAGO
# ---------------------
class ComprobantePagoForm(forms.ModelForm):
    """Formulario para subir comprobantes de pago"""
    class Meta:
        model = Pago
        fields = ['comprobante_pago', 'metodo_pago', 'monto', 'notas']
        widgets = {
            'comprobante_pago': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*,.pdf'
            }),
            'metodo_pago': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'monto': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Monto pagado'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Notas adicionales sobre el pago'
            })
        }

# ---------------------
# FORMULARIOS DE PAGOS
# ---------------------
class PagoForm(forms.ModelForm):
    """Formulario para pagos"""
    class Meta:
        model = Pago
        fields = ['monto', 'metodo_pago', 'comprobante_pago', 'notas']
        widgets = {
            'monto': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '0.01',
                'step': '0.01'
            }),
            'metodo_pago': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'comprobante_pago': forms.FileInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
            'notas': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3
            })
        }

# ---------------------
# FORMULARIOS DE COMPRA
# ---------------------
class CompraTicketForm(forms.Form):
    """Formulario para comprar tickets"""
    cantidad = forms.IntegerField(
        min_value=1,
        max_value=10,
        initial=1,
        label="Cantidad de Tickets",
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'min': '1',
            'max': '10'
        })
    )
    metodo_pago = forms.ChoiceField(
        choices=[
            ('efectivo', 'Efectivo'),
            ('transferencia', 'Transferencia'),
            ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ],
        label="Método de Pago",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )

class InscripcionSanForm(forms.Form):
    """Formulario para inscribirse en un san"""
    metodo_pago = forms.ChoiceField(
        choices=[
            ('efectivo', 'Efectivo'),
            ('transferencia', 'Transferencia'),
            ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ],
        label="Método de Pago",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    acepto_terminos = forms.BooleanField(
        required=True,
        label="Acepto los términos y condiciones",
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2'
        })
    )

# ---------------------
# FORMULARIOS DE BÚSQUEDA
# ---------------------
class BusquedaRifasForm(forms.Form):
    """Formulario de búsqueda para rifas"""
    q = forms.CharField(
        required=False,
        label="Buscar",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Buscar rifas...'
        })
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('recent', 'Más recientes'),
            ('price_low', 'Precio menor'),
            ('price_high', 'Precio mayor'),
            ('ending_soon', 'Terminando pronto'),
        ],
        label="Ordenar por",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )

class BusquedaSanesForm(forms.Form):
    """Formulario de búsqueda para sanes"""
    q = forms.CharField(
        required=False,
        label="Buscar",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Buscar sanes...'
        })
    )
    tipo = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todos los tipos'),
            ('ahorro', 'Ahorro'),
            ('producto', 'Producto'),
            ('servicio', 'Servicio'),
        ],
        label="Tipo",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('recent', 'Más recientes'),
            ('price_low', 'Precio menor'),
            ('price_high', 'Precio mayor'),
            ('participants', 'Más participantes'),
        ],
        label="Ordenar por",
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )