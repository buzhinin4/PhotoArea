from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RegisterView, LoginAPIView,
    LogoutAPIView, ChangePasswordView,
    StudioViewSet, PhotographerViewSet,
    RegularUserViewSet,
)
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

app_name = 'users'

router = DefaultRouter()
router.register(r'studios', StudioViewSet, basename='studio')
router.register(r'photographers', PhotographerViewSet, basename='photographer')
router.register(r'regular_users', RegularUserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='registration'),
    path('token/', LoginAPIView.as_view(), name='auth'),    # login
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

]
