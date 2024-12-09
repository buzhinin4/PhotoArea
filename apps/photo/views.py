from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.photo.models import Photo
from apps.photo.serializers.serializers import PhotoSerializer


class PhotoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [IsAuthenticated]
