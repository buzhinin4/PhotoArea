from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import NewViewSet

app_name = 'news'

router = DefaultRouter()
router.register(r'', NewViewSet, basename='news')

urlpatterns = [
    path('', include(router.urls)),
]
