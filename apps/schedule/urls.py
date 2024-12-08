from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ScheduleViewSet

app_name = 'schedule'

router = DefaultRouter()
router.register(r'', ScheduleViewSet, basename='schedule')

urlpatterns = [
    path('', include(router.urls)),
]
