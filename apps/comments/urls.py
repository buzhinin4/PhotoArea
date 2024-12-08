from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CommentAPIView

app_name = 'comments'

router = DefaultRouter()
router.register(r'', CommentAPIView)

urlpatterns = [
    path('', include(router.urls)),
]
