from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from apps.news.models import New
from apps.news.pagination.pagination import NewsPagination
from apps.news.serializers.serializers import NewSerializer, NewCreateSerializer


class NewViewSet(viewsets.ModelViewSet):
    queryset = New.objects.all()
    pagination_class = NewsPagination

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return NewCreateSerializer
        return NewSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        new_instance = serializer.instance
        response_serializer = NewSerializer(new_instance)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'partial': partial})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        page = request.query_params.get('page', None)
        page_size = request.query_params.get('page_size', None)

        if page or page_size:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        return Response(data, status=status.HTTP_200_OK)
