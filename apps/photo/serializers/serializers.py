from rest_framework import serializers

from apps.photo.models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ['id', 'url']

    def get_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
