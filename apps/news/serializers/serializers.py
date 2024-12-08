from rest_framework import serializers

from apps.news.models import New
from apps.photo.models import Photo
from apps.photo.serializers.serializers import PhotoSerializer
from apps.users.models import User


class NewCreateSerializer(serializers.ModelSerializer):
    photo_upload = serializers.ImageField(write_only=True, required=False, help_text="Загрузить новую фотографию")
    existing_photo = serializers.PrimaryKeyRelatedField(
        queryset=Photo.objects.all(),
        write_only=True,
        required=False,
        help_text="Выбрать существующую фотографию по ID"
    )
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = New
        fields = ['id', 'title', 'text', 'author', 'photo_upload', 'existing_photo']

    def validate(self, data):
        photo_upload = data.get('photo_upload')
        existing_photo = data.get('existing_photo')

        request = self.context.get('request')

        author = data.get('author', None)
        user = request.user

        if author is None:
            author = user

        # if not photo_upload and not existing_photo:
        #     raise serializers.ValidationError("Необходимо загрузить новую фотографию или выбрать существующую.")

        if photo_upload and existing_photo:
            raise serializers.ValidationError(
                "Выберите либо загрузить новую фотографию, либо выбрать существующую, но не оба варианта одновременно."
            )

        return data

    def create(self, validated_data):
        photo_upload = validated_data.pop('photo_upload', None)
        existing_photo = validated_data.pop('existing_photo', None)

        new = New.objects.create(**validated_data)

        if photo_upload:
            photo = Photo(image=photo_upload)
            photo.new_info = {'author': new.author, 'title': new.title}
            photo.save()
            new.photo = photo
            new.save()
        elif existing_photo:
            new.photo = existing_photo
            new.save()

        return new

    def update(self, instance, validated_data):
        photo_upload = validated_data.pop('photo_upload', None)
        existing_photo = validated_data.pop('existing_photo', None)

        if photo_upload:
            if instance.photo:
                instance.photo.delete()
                photo = Photo(image=photo_upload)
                photo.new_info = {'author': instance.author, 'title': instance.title}
                photo.save()
                instance.photo = photo
                instance.save()
            else:
                photo = Photo(image=photo_upload)
                photo.new_info = {'author': instance.author, 'title': instance.title}
                photo.save()
                instance.photo = photo
                instance.save()
        elif existing_photo:
            instance.photo = existing_photo

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class NewSerializer(serializers.ModelSerializer):
    photo = PhotoSerializer(required=False, allow_null=True)

    class Meta:
        model = New
        fields = '__all__'


# class NewCreateSerializer(serializers.ModelSerializer):
#     photo_upload = serializers.ImageField(write_only=True, required=False)
#     existing_photo = serializers.PrimaryKeyRelatedField(
#         queryset=Photo.objects.all(),
#         write_only=True,
#         required=False
#     )
#
#     class Meta:
#         model = New
#         fields = ['id', 'title', 'text', 'author', 'photo_upload', 'existing_photo']
#
#     def validate(self, data):
#         photo_upload = data.get('photo_upload')
#         existing_photo = data.get('existing_photo')
#
#         if not photo_upload and not existing_photo:
#             raise serializers.ValidationError("Необходимо загрузить новую фотографию или выбрать существующую.")
#
#         if photo_upload and existing_photo:
#             raise serializers.ValidationError(
#                 "Выберите либо загрузить новую фотографию, либо выбрать существующую, но не оба варианта одновременно.")
#
#         return data
#
#     def create(self, validated_data):
#         photo_upload = validated_data.pop('photo_upload', None)
#         existing_photo = validated_data.pop('existing_photo', None)
#         new = New.objects.create(**validated_data)
#
#         if photo_upload:
#             photo = Photo.objects.create(image=photo_upload)
#             new.photo = photo
#             new.save()
#         elif existing_photo:
#             new.photo = existing_photo
#             new.save()
#
#         return new
#
#     def update(self, instance, validated_data):
#         photo_upload = validated_data.pop('photo_upload', None)
#         existing_photo = validated_data.pop('existing_photo', None)
#
#         if photo_upload:
#             if instance.photo:
#                 instance.photo.image = photo_upload
#                 instance.photo.save()
#             else:
#                 photo = Photo.objects.create(image=photo_upload)
#                 instance.photo = photo
#         elif existing_photo:
#             instance.photo = existing_photo
#
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#
#         instance.save()
#         return instance

# class NewCreateSerializer(serializers.ModelSerializer):
#     photo_upload = serializers.ImageField(write_only=True, required=False, help_text="Загрузить новую фотографию")
#     existing_photo = serializers.PrimaryKeyRelatedField(
#         queryset=Photo.objects.all(),
#         write_only=True,
#         required=False,
#         allow_null=True,  # Добавлено
#         help_text="Выбрать существующую фотографию по ID"
#     )
#
#     class Meta:
#         model = New
#         fields = ['id', 'title', 'text', 'author', 'photo_upload', 'existing_photo']
#
#     def validate(self, data):
#         photo_upload = data.get('photo_upload')
#         existing_photo = data.get('existing_photo')
#
#         if not photo_upload and not existing_photo:
#             raise serializers.ValidationError("Необходимо загрузить новую фотографию или выбрать существующую.")
#
#         if photo_upload and existing_photo:
#             raise serializers.ValidationError(
#                 "Выберите либо загрузить новую фотографию, либо выбрать существующую, но не оба варианта одновременно."
#             )
#
#         return data
#
#     def create(self, validated_data):
#         photo_upload = validated_data.pop('photo_upload', None)
#         existing_photo = validated_data.pop('existing_photo', None)
#
#         # Создаём экземпляр New без сохранения его поля photo
#         new = New.objects.create(**validated_data)
#
#         if photo_upload:
#             # Создаём Photo и устанавливаем временный атрибут 'new_title'
#             photo = Photo(image=photo_upload)
#             photo.new_title = new.title  # Временный атрибут для пути загрузки
#             photo.save()
#             # Связываем Photo с New
#             new.photo = photo
#             new.save()
#         elif existing_photo:
#             # Связываем существующую Photo с New
#             new.photo = existing_photo
#             new.save()
#
#         return new
#
#     def update(self, instance, validated_data):
#         photo_upload = validated_data.pop('photo_upload', None)
#         existing_photo = validated_data.pop('existing_photo', None)
#
#         if photo_upload:
#             if instance.photo:
#                 # Обновляем существующую фотографию
#                 instance.photo.image = photo_upload
#                 instance.photo.new_title = instance.title  # Устанавливаем временный атрибут
#                 instance.photo.save()
#             else:
#                 # Создаём новую фотографию с временным атрибутом
#                 photo = Photo(image=photo_upload)
#                 photo.new_title = instance.title  # Временный атрибут для пути загрузки
#                 photo.save()
#                 instance.photo = photo
#         elif existing_photo:
#             # Связываем существующую фотографию
#             instance.photo = existing_photo
#
#         # Обновляем остальные поля
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#
#         instance.save()
#         return instance