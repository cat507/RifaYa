from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Busca el usuario por correo
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None
        
        # Verifica la contraseña
        if user.check_password(password):
            return user
        
        return None
