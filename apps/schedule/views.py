from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from apps.schedule.models import Schedule
from apps.schedule.serializers.serializers import (
    ScheduleSerializer, CreateScheduleSerializer,
)
from rest_framework.response import Response
from apps.users.permissions.permissions import IsExecutor


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateScheduleSerializer
        return ScheduleSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsExecutor]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        if 'executor' not in request.data.keys():
            request.data['executor'] = None
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        new_instance = serializer.instance
        response_serializer = ScheduleSerializer(new_instance, context={'request': request})

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if 'executor' not in request.data.keys():
            request.data['executor'] = None
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_serializer = ScheduleSerializer(serializer.instance, context={'request': request})

        return Response(response_serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)
