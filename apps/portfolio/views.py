from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Portfolio, Studio, Photographer
from .serializers.serializers import PortfolioSerializer
from ..users.permissions.permissions import IsExecutor


class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer
    permission_classes = [IsExecutor]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'studio_profile'):
            return Portfolio.objects.filter(studio=user.studio_profile)
        elif hasattr(user, 'photographer_profile'):
            return Portfolio.objects.filter(photographer=user.photographer_profile)
        return Portfolio.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        if hasattr(user, 'studio_profile'):
            studio = user.studio_profile
            if serializer.validated_data.get('studio') and serializer.validated_data['studio'] != studio:
                raise PermissionDenied("Вы можете создавать портфолио только для своей студии.")
            serializer.save(studio=studio)
        elif hasattr(user, 'photographer_profile'):
            photographer = user.photographer_profile
            if serializer.validated_data.get('photographer') and serializer.validated_data['photographer'] != photographer:
                raise PermissionDenied("Вы можете создавать портфолио только для себя как фотограф.")
            serializer.save(photographer=photographer)
        else:
            raise PermissionDenied("Вы должны быть студией или фотографом для создания портфолио.")
