from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class UsernameOrEmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Перевірка за username або email
            user = User.objects.get(username=username) if User.objects.filter(username=username).exists() else User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
