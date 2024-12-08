from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from apps.users.permissions.permissions import IsClient
from apps.order.models import Order
from rest_framework.response import Response
from apps.order.serializers.serializers import (
    OrderSerializer, CreateOrderSerializer,
)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateOrderSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            permissions_classes = [IsClient]
        else:
            permissions_classes = [permissions.IsAuthenticated]
        return [permissions() for permissions in permissions_classes]

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        if 'client' not in request.data.keys():
            request.data['client'] = None
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        new_instance = serializer.instance
        response_serializer = OrderSerializer(new_instance, context={'request': request})

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if 'client' not in request.data.keys():
            request.data['client'] = None
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_serializer = OrderSerializer(serializer.instance, context={'request': request})

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