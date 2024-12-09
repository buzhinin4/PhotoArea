from django.contrib.auth import get_user_model
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.exceptions import ValidationError

from apps.users.models import Studio, Photographer
from apps.users.permissions.permissions import IsOwner
from apps.users.serializers import (
    CustomTokenObtainPairSerializer,
    LogoutSerializer, ChangePasswordSerializer,
    BaseRegisterSerializer, PhotographerRegisterSerializer,
    StudioRegisterSerializer, RegularUserRegisterSerializer,
    StudioSerializer, PhotographerSerializer,
    RegularUserSerializer,
)
from apps.users.services.services import AuthService
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=ChangePasswordSerializer,
        responses={200: None},
    )
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get("new_password"))
            user.save()

            refresh_token = serializer.data.get("refresh")

            try:
                AuthService.logout_user(refresh_token)
                return Response({"detail": "Password has been changed successfully and you have been logged out."},
                                status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_204_NO_CONTENT)


class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (AllowAny,)
    serializer_class = BaseRegisterSerializer

    def get_serializer_class(self):
        user_type = self.request.data.get('user_type')
        if user_type == 'photographer':
            return PhotographerRegisterSerializer
        elif user_type == 'studio':
            return StudioRegisterSerializer
        return RegularUserRegisterSerializer


class StudioViewSet(viewsets.ModelViewSet):
    queryset = Studio.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return StudioRegisterSerializer
        return StudioSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwner]
        if self.action in ['create']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    # @extend_schema(
    #     operation_id="Create Studio",
    #     description="Endpoint to create a new studio with optional photo upload.",
    #     request={
    #         "multipart/form-data": OpenApiTypes.OBJECT,
    #         "application/json": OpenApiTypes.OBJECT,
    #     },
    #     parameters=[
    #         OpenApiParameter(
    #             name="email",
    #             type=OpenApiTypes.STR,
    #             description="Email of the studio",
    #             required=True,
    #         ),
    #         OpenApiParameter(
    #             name="phone_number",
    #             type=OpenApiTypes.STR,
    #             description="Phone number of the studio",
    #             required=True,
    #         ),
    #         OpenApiParameter(
    #             name="name",
    #             type=OpenApiTypes.STR,
    #             description="Name of the studio",
    #             required=True,
    #         ),
    #         OpenApiParameter(
    #             name="description",
    #             type=OpenApiTypes.STR,
    #             description="Description of the studio",
    #             required=False,
    #         ),
    #         OpenApiParameter(
    #             name="address.city",
    #             type=OpenApiTypes.STR,
    #             description="City of the studio",
    #             required=True,
    #         ),
    #         OpenApiParameter(
    #             name="address.street",
    #             type=OpenApiTypes.STR,
    #             description="Street of the studio",
    #             required=True,
    #         ),
    #         OpenApiParameter(
    #             name="address.building",
    #             type=OpenApiTypes.STR,
    #             description="Building of the studio",
    #             required=True,
    #         ),
    #         OpenApiParameter(
    #             name="address.office",
    #             type=OpenApiTypes.STR,
    #             description="Office of the studio",
    #             required=False,
    #         ),
    #         OpenApiParameter(
    #             name="photo_upload",
    #             type=OpenApiTypes.BINARY,
    #             description="Photo to upload",
    #             required=False,
    #         ),
    #     ],
    #     examples=[
    #         OpenApiExample(
    #             name="Example with photo upload",
    #             value={
    #                 "email": "Studio5@example.com",
    #                 "phone_number": "+375333507228",
    #                 "name": "Studio5",
    #                 "description": "Studio5 description",
    #                 "address": {
    #                     "city": "Minsk",
    #                     "street": "Lenina",
    #                     "building": "10",
    #                     "office": "5A"
    #                 },
    #                 "photo_upload": "binary file content here"
    #             },
    #             request_only=True,
    #         ),
    #         OpenApiExample(
    #             name="Example without photo",
    #             value={
    #                 "email": "Studio5@example.com",
    #                 "phone_number": "+375333507228",
    #                 "name": "Studio5",
    #                 "description": "Studio5 description",
    #                 "address": {
    #                     "city": "Minsk",
    #                     "street": "Lenina",
    #                     "building": "10",
    #                     "office": "5A"
    #                 }
    #             },
    #             request_only=True,
    #         ),
    #     ],
    # )
    def create(self, request, *args, **kwargs):
        factory = APIRequestFactory()
        register_data = {
            **request.data,
            'user_type': 'studio'
        }
        new_request = factory.post(
            request.path,
            data=register_data,
            format='multipart'
        )
        register_view = RegisterView.as_view()
        response = register_view(new_request)

        if response.status_code == 201:
            studio = Studio.objects.get(base_user__email=register_data.get('email')[0])
            serializer = StudioSerializer(studio, context={'request': request})
            return Response(serializer.data, status=response.status_code)
        return response

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_serializer = StudioSerializer(instance, context={'request': request})
        return Response(response_serializer.data)


class PhotographerViewSet(viewsets.ModelViewSet):
    queryset = Photographer.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PhotographerRegisterSerializer
        return PhotographerSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwner]
        if self.action in ['create']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        factory = APIRequestFactory()
        register_data = {
            **request.data,
            'user_type': 'photographer'
        }
        new_request = factory.post(
            request.path,
            data=register_data,
            format='multipart'
        )
        register_view = RegisterView.as_view()
        response = register_view(new_request)

        if response.status_code == 201:
            photographer = Photographer.objects.get(base_user__email=register_data.get('email')[0])
            serializer = PhotographerSerializer(photographer, context={'request': request})
            return Response(serializer.data, status=response.status_code)
        return response

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        response_serializer = PhotographerSerializer(instance, context={'request': request})
        return Response(response_serializer.data)


class RegularUserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.filter(Q(user_type=3) | Q(user_type__isnull=True))
    serializer_class = RegularUserSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        register_data = {
            **request.data,
            'user_type': None
        }
        register_view = RegisterView.as_view()
        request.data = register_data
        response = register_view(request=request, user_type=None)
        return response


class UserDetailAPIView(generics.RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        user_type = self.get_user_type()
        if user_type == 'photographer':
            return PhotographerSerializer
        elif user_type == 'studio':
            return StudioSerializer
        return RegularUserSerializer

    def get_user_type(self):
        user = self.request.user
        if hasattr(user, 'studio_profile'):
            return 'studio'
        elif hasattr(user, 'photographer_profile'):
            return 'photographer'
        return 'regular'

    def get_object(self):
        user = self.request.user
        if hasattr(user, 'studio_profile'):
            return user.studio_profile
        elif hasattr(user, 'photographer_profile'):
            return user.photographer_profile
        return user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        return Response(data, status=status.HTTP_200_OK)
