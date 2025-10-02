from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Try to find the user by username or email
        try:
            user = CustomUser.objects.get(username=username)  # Try by username
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(email=username)  # Try by email if username not found
            except CustomUser.DoesNotExist:
                return None  # Return None if neither found
        
        # If the user is found, check the password
        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None