from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ValidationError


class AuthService:
    @staticmethod
    def logout_user(refresh_token: str):
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            raise ValidationError("Invalid refresh token") from e
