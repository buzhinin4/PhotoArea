from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import OrderViewSet

app_name = 'schedule'

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]