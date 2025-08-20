from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
# sanes/forms.py
from django import forms
from .models import Raffle  # Asegúrate de importar el modelo Raffle
from django import forms
from .models import San, Raffle, Comment
from allauth.account.forms import SignupForm
from django import forms
from .models import San, Raffle, Comment
from allauth.account.forms import SignupForm

from django import forms
from .models import Raffle

# sanes/forms.py
from django import forms
from .models import Raffle

class CambiarFotoPerfilForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['foto_perfil']

class RaffleForm(forms.ModelForm):
    class Meta:
        model = Raffle
        fields = [
            'description',
            'prize_name',
            'total_price',
            'num_cuotas',
            'fecha_fin',
            'image',
        ]
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#191010] focus:outline-0 focus:ring-0 border-none bg-[#f1e9ea] focus:border-none min-h-36 placeholder:text-[#8b5b5c] p-4 text-base font-normal leading-normal',
                'placeholder': 'Describe the prize in detail',
            }),
            'prize_name': forms.TextInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#191010] focus:outline-0 focus:ring-0 border-none bg-[#f1e9ea] focus:border-none h-14 placeholder:text-[#8b5b5c] p-4 text-base font-normal leading-normal',
                'placeholder': 'Enter the name of the prize',
            }),
            'total_price': forms.NumberInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#191010] focus:outline-0 focus:ring-0 border-none bg-[#f1e9ea] focus:border-none h-14 placeholder:text-[#8b5b5c] p-4 text-base font-normal leading-normal',
                'placeholder': 'Enter the total price of the prize',
            }),
            'num_cuotas': forms.NumberInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#191010] focus:outline-0 focus:ring-0 border-none bg-[#f1e9ea] focus:border-none h-14 placeholder:text-[#8b5b5c] p-4 text-base font-normal leading-normal',
                'placeholder': 'Enter the total number of tickets',
            }),
            'fecha_fin': forms.DateInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#191010] focus:outline-0 focus:ring-0 border-none bg-[#f1e9ea] focus:border-none h-14 placeholder:text-[#8b5b5c] p-4 text-base font-normal leading-normal',
                'type': 'datetime-local',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#191010] focus:outline-0 focus:ring-0 border-none bg-[#f1e9ea] focus:border-none h-14 placeholder:text-[#8b5b5c] p-4 text-base font-normal leading-normal',
            }),
        }

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label="Correo Electrónico o Usuario", max_length=254)
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    def clean_username(self):
        username_or_email = self.cleaned_data['username']
        return username_or_email  # No es necesario hacer validaciones adicionales aquí

class CustomUserCreationForm(UserCreationForm):
    cedula = forms.CharField(max_length=20, required=True, label="Cédula")
    oficio = forms.CharField(max_length=100, required=True, label="Oficio")
    telefono = forms.CharField(max_length=15, required=True, label="Teléfono")
    email = forms.EmailField(required=True, label="Correo Electrónico")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'cedula', 'oficio', 'telefono']

    def save(self, commit=True):
        user = super().save(commit)
        user.email = self.cleaned_data['email']
        user.cedula = self.cleaned_data['cedula']
        user.oficio = self.cleaned_data['oficio']
        user.phone_number = self.cleaned_data['telefono']
        if commit:
            user.save()
        return user

from django import forms

class ConfirmPurchaseForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('bank_transfer', 'Transferencia Bancaria'),
        ('cash', 'Efectivo'),
    ]
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect)
    payment_receipt = forms.ImageField(required=False, help_text="Sube una captura del pago si seleccionas transferencia bancaria.")

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get("payment_method")
        payment_receipt = cleaned_data.get("payment_receipt")

        # Verificar que la captura de pantalla esté presente si se selecciona transferencia bancaria
        if payment_method == 'bank_transfer' and not payment_receipt:
            raise forms.ValidationError("Debes subir una captura del pago para transferencia bancaria.")

from django import forms
from .models import San

class SanForm(forms.ModelForm):
    class Meta:
        model = San
        fields = [
            'name', 
            'organizador', 
            'fecha_inicio', 
            'total_price', 
            'num_cuotas', 
            'payment_frequency', 
            'type_of_san', 
            'image', 
            'total_participantes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del SAN o Producto'}),
            'organizador': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'total_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio Total'}),
            'num_cuotas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Número de Cuotas'}),
            'payment_frequency': forms.Select(attrs={'class': 'form-control'}),
            'type_of_san': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'total_participantes': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total de Participantes'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }
