from rest_framework import serializers
from ..models import Comment


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['destination', 'rate', 'title', 'body']

    def validate(self, attrs):
        return attrs


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['rate', 'title', 'body']

    def validate(self, attrs):
        partial = attrs.get('partial', False)

        return attrs


class CommentDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    destination = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'destination', 'rate', 'title', 'body', 'time_create', 'time_update']
        read_only_fields = ['id', 'author', 'destination', 'time_create', 'time_update']
