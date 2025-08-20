from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Intenta encontrar el usuario por email
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # Si no, intenta encontrarlo por nombre de usuario
            try:
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None
        
        if user.check_password(password):
            return user
        return None