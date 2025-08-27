from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_field, user_username
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        
        # Guardar campos adicionales del CustomUser
        if form.cleaned_data.get('first_name'):
            user.first_name = form.cleaned_data['first_name']
        if form.cleaned_data.get('last_name'):
            user.last_name = form.cleaned_data['last_name']
        if form.cleaned_data.get('phone_number'):
            user.phone_number = form.cleaned_data['phone_number']
        if form.cleaned_data.get('cedula'):
            user.cedula = form.cleaned_data['cedula']
        if form.cleaned_data.get('oficio'):
            user.oficio = form.cleaned_data['oficio']
        if form.cleaned_data.get('address'):
            user.address = form.cleaned_data['address']
        if form.cleaned_data.get('date_of_birth'):
            user.date_of_birth = form.cleaned_data['date_of_birth']
        
        if commit:
            user.save()
        return user

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        
        # Extraer información del perfil de Google
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data
            
            # Nombre completo
            if 'name' in extra_data:
                name_parts = extra_data['name'].split(' ', 1)
                user.first_name = name_parts[0]
                if len(name_parts) > 1:
                    user.last_name = name_parts[1]
            
            # Email
            if 'email' in extra_data:
                user.email = extra_data['email']
            
            # Username basado en email
            if 'email' in extra_data:
                user.username = extra_data['email'].split('@')[0]
            
            # Foto de perfil
            if 'picture' in extra_data:
                user.foto_perfil = extra_data['picture']
        
        return user

    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        
        # Asegurar que el usuario tenga un username único
        if not user.username:
            base_username = user.email.split('@')[0] if user.email else 'user'
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user.username = username
        
        return user

