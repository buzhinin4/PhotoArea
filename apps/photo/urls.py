from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.photo.views import PhotoViewSet

app_name = 'photos'

router = DefaultRouter()
router.register(r'', PhotoViewSet, basename='photo')

urlpatterns = [
    path('', include(router.urls)),
]
