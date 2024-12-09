from rest_framework import serializers
from apps.photo.models import Photo
from apps.portfolio.models import Portfolio, PortfolioPhotos


class PortfolioSerializer(serializers.ModelSerializer):
    photos = serializers.SerializerMethodField()
    photo_upload = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        help_text="Upload new photos"
    )
    existing_photos = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Photo.objects.all()),
        write_only=True,
        required=False,
        help_text="List of existing photo IDs"
    )
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ['id', 'description', 'photos', 'photo_upload', 'existing_photos', 'owner']
        read_only_fields = ['owner', 'photos']

    def get_photos(self, obj):
        return [{
            'id': photo.id,
            'url': photo.image.url
        } for photo in obj.photos.all() if photo.image]

    def get_owner(self, obj):
        if obj.studio:
            return {'type': 'studio', 'id': obj.studio.id, 'name': obj.studio.name}
        elif obj.photographer:
            return {'type': 'photographer', 'id': obj.photographer.id, 'description': obj.photographer.description}
        return None

    def validate(self, data):
        user = self.context['request'].user
        if not hasattr(user, 'studio_profile') and not hasattr(user, 'photographer_profile'):
            raise serializers.ValidationError("Вы должны быть студией или фотографом, чтобы создать портфолио.")

        return data

    def create(self, validated_data):
        photo_upload = validated_data.pop('photo_upload', [])
        existing_photos = validated_data.pop('existing_photos', [])
        user = self.context['request'].user

        if hasattr(user, 'studio_profile'):
            validated_data.pop('studio', None)
            portfolio = Portfolio.objects.create(studio=user.studio_profile, **validated_data)
        elif hasattr(user, 'photographer_profile'):
            validated_data.pop('photographer', None)
            portfolio = Portfolio.objects.create(photographer=user.photographer_profile, **validated_data)
        else:
            raise serializers.ValidationError({"owner": "Пользователь должен быть студией или фотографом для создания портфолио."})

        for photo in existing_photos:
            PortfolioPhotos.objects.create(portfolio=portfolio, photo=photo)

        for photo_file in photo_upload:
            photo = Photo(image=photo_file)
            photo_file.portfolio_info = {'username': user.email}
            photo_file.portfolio_info = {'portfolio_id': portfolio.pk}
            photo.save()
            PortfolioPhotos.objects.create(portfolio=portfolio, photo=photo)

        return portfolio

    def update(self, instance, validated_data):
        photo_upload = validated_data.pop('photo_upload', [])
        existing_photos = validated_data.pop('existing_photos', [])
        user = self.context['request'].user

        if instance.studio and instance.studio != getattr(user, 'studio_profile', None):
            raise serializers.ValidationError({"owner": "Вы можете обновлять только свои портфолио."})
        if instance.photographer and instance.photographer != getattr(user, 'photographer_profile', None):
            raise serializers.ValidationError({"owner": "Вы можете обновлять только свои портфолио."})

        instance.description = validated_data.get('description', instance.description)

        new_uploaded_photos = []

        for photo_file in photo_upload:
            photo = Photo(image=photo_file)
            photo.portfolio_info = {'username': user.email, 'portfolio_id': instance.pk}
            photo.save()
            PortfolioPhotos.objects.create(portfolio=instance, photo=photo)
            new_uploaded_photos.append(photo)

        for photo in existing_photos:
            if not PortfolioPhotos.objects.filter(portfolio=instance, photo=photo).exists():
                PortfolioPhotos.objects.create(portfolio=instance, photo=photo)

        current_photos = set(instance.photos.all())
        new_photos = set(existing_photos) | set(new_uploaded_photos)
        photos_to_remove = current_photos - new_photos

        for photo in photos_to_remove:
            PortfolioPhotos.objects.filter(portfolio=instance, photo=photo).delete()

        instance.save()
        return instance

