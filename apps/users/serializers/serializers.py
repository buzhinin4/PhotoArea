from collections import defaultdict

from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Avg
from datetime import datetime, timedelta

from apps.address.models import Address
from apps.address.serializers import AddressSerializer
from apps.order.models import Order
from apps.photo.models import Photo
from apps.schedule.models import Schedule
from apps.users.models import UserType, Studio, Photographer
from apps.users.services.services import AuthService


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

    def validate(self, attrs):
        self.refresh_token = attrs.get('refresh')
        if not self.refresh_token:
            raise serializers.ValidationError("Refresh token is required")
        return attrs

    def save(self, **kwargs):
        if self.refresh_token:
            try:
                AuthService.logout_user(self.refresh_token)
            except serializers.ValidationError as e:
                self.fail('bad_refresh_token')


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    refresh = serializers.CharField(required=True)

    class Meta:
        fields = ('old_password', 'new_password', 'refresh',)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = get_user_model().objects.filter(email=email).first()
        if not user or not authenticate(email=email, password=password):
            raise serializers.ValidationError({
                'email': 'No active account found with the given credentials',
                'password': 'No active account found with the given credentials'
            })

        return super().validate(attrs)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['email'] = user.email

        return token


class BaseRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=get_user_model().objects.all())]
    )

    class Meta:
        model = get_user_model()
        fields = (
            'username', 'email', 'password', 'password2',
            'phone_number', 'photo', 'first_name', 'last_name', 'date_birth'
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": 'Passwords do not match'})
        return attrs

    def create_user(self, validated_data, user_type_name=None):
        password = validated_data.pop('password')
        validated_data.pop('password2')
        if user_type_name is not None:
            user_type = UserType.objects.get(name=user_type_name)
        else:
            user_type = None
        user = get_user_model().objects.create_user(user_type=user_type, **validated_data)
        user.set_password(password)
        user.save()
        return user


class StudioRegisterSerializer(BaseRegisterSerializer):
    name = serializers.CharField(write_only=True, required=True)
    description = serializers.CharField(write_only=True, required=False, allow_blank=True)
    address = AddressSerializer(write_only=True, required=True)
    photo_upload = serializers.ImageField(write_only=True, required=False, help_text="Загрузить новую фотографию")
    existing_photo = serializers.PrimaryKeyRelatedField(
        queryset=Photo.objects.all(),
        write_only=True,
        required=False,
        help_text="Выбрать существующую фотографию по ID"
    )

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + ('name', 'description', 'address', 'photo_upload', 'existing_photo')

    def validate(self, attrs):
        if self.instance:
            return self.validate_update(attrs)
        return self.validate_create(attrs)

    def validate_create(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get('name'):
            raise serializers.ValidationError({"name": "No studio name provided"})
        if not attrs.get('address'):
            raise serializers.ValidationError({"address": "No studio address provided"})

        photo_upload = attrs.get('photo_upload')
        existing_photo = attrs.get('existing_photo')
        if photo_upload and existing_photo:
            raise serializers.ValidationError(
                "Выберите либо загрузить новую фотографию, либо выбрать существующую, но не оба варианта одновременно."
            )

        return attrs

    def validate_update(self, attrs):
        """
        Валидация для обновления.
        """
        photo_upload = attrs.get('photo_upload')
        existing_photo = attrs.get('existing_photo')

        if photo_upload and existing_photo:
            raise serializers.ValidationError(
                "Выберите либо загрузить новую фотографию, либо выбрать существующую, но не оба варианта одновременно."
            )

        # Дополнительные проверки для обновления, если нужны
        return attrs

    # def validate(self, attrs):
    #     attrs = super().validate(attrs)
    #     if not attrs.get('name'):
    #         raise serializers.ValidationError({"name": 'No studio name provided'})
    #     if not attrs.get('address'):
    #         raise serializers.ValidationError({"address": 'No studio address provided'})
    #
    #     photo_upload = attrs.get('photo_upload')
    #     existing_photo = attrs.get('existing_photo')
    #     if photo_upload and existing_photo:
    #         raise serializers.ValidationError(
    #             "Выберите либо загрузить новую фотографию, либо выбрать существующую, но не оба варианта одновременно."
    #         )
    #
    #     return attrs

    def create(self, validated_data):
        studio_name = validated_data.pop('name')
        studio_description = validated_data.pop('description', '')
        studio_address_data = validated_data.pop('address')
        photo_upload = validated_data.pop('photo_upload', None)
        existing_photo = validated_data.pop('existing_photo', None)

        user = self.create_user(validated_data, user_type_name='studio')
        address = Address.objects.create(**studio_address_data)

        Studio.objects.create(
            name=studio_name,
            description=studio_description,
            address=address,
            base_user=user
        )

        if photo_upload:
            photo = Photo(image=photo_upload)
            photo.user_info = {'username': user.email}
            photo.save()
            user.photo = photo
            user.photo = photo
        elif existing_photo:
            user.photo = existing_photo

        user.save()
        return user

    def update(self, instance, validated_data):
        studio_name = validated_data.pop('name', None)
        studio_description = validated_data.pop('description', None)
        studio_address_data = validated_data.pop('address', None)
        photo_upload = validated_data.pop('photo_upload', None)
        existing_photo = validated_data.pop('existing_photo', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        studio = instance
        if studio_name:
            studio.name = studio_name
        if studio_description is not None:
            studio.description = studio_description
        if studio_address_data:
            address = studio.address
            for attr, value in studio_address_data.items():
                setattr(address, attr, value)
            address.save()

        studio.save()

        bu_instance = instance.base_user
        if photo_upload:
            if bu_instance.photo:
                bu_instance.photo.delete()
            photo = Photo(image=photo_upload)
            photo.user_info = {'username': bu_instance.email}
            photo.save()
            bu_instance.photo = photo
        elif existing_photo:
            bu_instance.photo = existing_photo
        bu_instance.save()
        instance.save()
        return instance


class PhotographerRegisterSerializer(BaseRegisterSerializer):
    description = serializers.CharField(write_only=True, required=True)
    photo_upload = serializers.ImageField(write_only=True, required=False, help_text="Загрузить новую фотографию")
    existing_photo = serializers.PrimaryKeyRelatedField(
        queryset=Photo.objects.all(),
        write_only=True,
        required=False,
        help_text="Выбрать существующую фотографию по ID"
    )

    class Meta(BaseRegisterSerializer.Meta):
        fields = BaseRegisterSerializer.Meta.fields + ('description', 'photo_upload', 'existing_photo')

    def validate(self, attrs):
        if self.instance:
            return self.validate_update(attrs)
        return self.validate_create(attrs)

    def validate_create(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get('description'):
            raise serializers.ValidationError({"description": 'No photographer description provided'})

        photo_upload = attrs.get('photo_upload')
        existing_photo = attrs.get('existing_photo')
        if photo_upload and existing_photo:
            raise serializers.ValidationError(
                "Выберите либо загрузить новую фотографию, либо выбрать существующую, но не оба варианта одновременно."
            )

        return attrs

    def validate_update(self, attrs):
        photo_upload = attrs.get('photo_upload')
        existing_photo = attrs.get('existing_photo')

        if photo_upload and existing_photo:
            raise serializers.ValidationError(
                "Выберите либо загрузить новую фотографию, либо выбрать существующую, но не оба варианта одновременно."
            )

        return attrs

    def create(self, validated_data):
        photographer_description = validated_data.pop('description')
        photo_upload = validated_data.pop('photo_upload', None)
        existing_photo = validated_data.pop('existing_photo', None)

        user = self.create_user(validated_data, user_type_name='photographer')

        Photographer.objects.create(
            base_user=user,
            description=photographer_description
        )

        if photo_upload:
            photo = Photo(image=photo_upload)
            photo.user_info = {'username': user.email}
            photo.save()
            user.photo = photo
        elif existing_photo:
            user.photo = existing_photo

        user.save()
        return user

    def update(self, instance, validated_data):
        photographer_description = validated_data.pop('description', None)
        photo_upload = validated_data.pop('photo_upload', None)
        existing_photo = validated_data.pop('existing_photo', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        photographer = instance
        if photographer_description:
            photographer.description = photographer_description
        photographer.save()

        bu_instance = instance.base_user
        if photo_upload:
            if bu_instance.photo:
                bu_instance.photo.delete()
            photo = Photo(image=photo_upload)
            photo.user_info = {'username': bu_instance.email}
            photo.save()
            bu_instance.photo = photo
        elif existing_photo:
            bu_instance.photo = existing_photo
        bu_instance.save()

        instance.save()
        return instance


class RegularUserRegisterSerializer(BaseRegisterSerializer):
    class Meta(BaseRegisterSerializer.Meta):
        pass

    def create(self, validated_data):
        return self.create_user(validated_data)


class StudioSerializer(serializers.ModelSerializer):
    rate = serializers.SerializerMethodField()
    portfolios = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    base_user_id = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    available_slots = serializers.SerializerMethodField()
    schedules = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()

    def get_rate(self, obj):
        comments = obj.base_user.comments.all()
        if comments.exists():
            avg_rate = comments.aggregate(Avg('rate'))['rate__avg']
            return round(avg_rate, 2)
        return None

    def get_portfolios(self, obj):
        portfolios = obj.portfolios.all()
        if portfolios.exists():
            id_list = [portfolio.pk for portfolio in portfolios]
            return id_list
        return []

    def get_comments(self, obj):
        comments = obj.base_user.comments.all()
        if comments.exists():
            id_list = [comment.pk for comment in comments]
            return id_list
        return []

    def get_base_user_id(self, obj):
        return obj.base_user.id

    def address(self, obj):
        addresses = obj.base_user.address.all()
        if addresses.exists():
            id_list = [address.pk for address in addresses]
            return id_list
        return []

    def get_schedules(self, obj):
        schedules = Schedule.objects.filter(executor=obj.base_user)
        if schedules.exists():
            id_list = [schedule.pk for schedule in schedules]
            return id_list
        return []

    def get_available_slots(self, obj):
        today = datetime.now().date()
        two_weeks_later = today + timedelta(weeks=2)

        schedules = Schedule.objects.filter(executor=obj.base_user)

        orders = Order.objects.filter(
            executor=obj.base_user,
            date__gte=today,
            date__lte=two_weeks_later
        ).values('date', 'schedule_id')

        occupied_slots = defaultdict(list)
        for order in orders:
            occupied_slots[order['date']].append(order['schedule_id'])

        available_slots = defaultdict(list)

        for day_offset in range(15):
            current_date = today + timedelta(days=day_offset)
            weekday = (current_date.weekday() + 1) % 7 or 7

            day_schedules = schedules.filter(weekday=weekday)
            for schedule in day_schedules:

                if schedule.id not in occupied_slots.get(current_date, []):
                    available_slots[current_date.isoformat()].append(schedule.id)

        return dict(available_slots)

    def get_photo(self, obj):
        if obj.base_user.photo and obj.base_user.photo.image:
            return obj.base_user.photo.pk
        return None

    def get_user_type(self, obj):
        return 'studio'

    class Meta:
        model = Studio
        fields = '__all__'


class PhotographerSerializer(serializers.ModelSerializer):
    rate = serializers.SerializerMethodField()
    portfolios = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    base_user_id = serializers.SerializerMethodField()
    available_slots = serializers.SerializerMethodField()
    schedules = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()

    def get_rate(self, obj):
        comments = obj.base_user.comments.all()
        if comments.exists():
            avg_rate = comments.aggregate(Avg('rate'))['rate__avg']
            return round(avg_rate, 2)
        return None

    def get_portfolios(self, obj):
        portfolios = obj.portfolios.all()
        if portfolios.exists():
            id_list = [portfolio.pk for portfolio in portfolios]
            return id_list
        return []

    def get_comments(self, obj):
        comments = obj.base_user.comments.all()
        if comments.exists():
            id_list = [comment.pk for comment in comments]
            return id_list
        return []

    def get_base_user_id(self, obj):
        return obj.base_user.id

    def get_schedules(self, obj):
        schedules = Schedule.objects.filter(executor=obj.base_user)
        if schedules.exists():
            id_list = [schedule.pk for schedule in schedules]
            return id_list
        return []

    def get_available_slots(self, obj):
        today = datetime.now().date()
        two_weeks_later = today + timedelta(weeks=2)

        schedules = Schedule.objects.filter(executor=obj.base_user)

        orders = Order.objects.filter(
            executor=obj.base_user,
            date__gte=today,
            date__lte=two_weeks_later
        ).values('date', 'schedule_id')

        occupied_slots = defaultdict(list)
        for order in orders:
            occupied_slots[order['date']].append(order['schedule_id'])

        available_slots = defaultdict(list)

        for day_offset in range(15):
            current_date = today + timedelta(days=day_offset)
            weekday = (current_date.weekday() + 1) % 7 or 7

            day_schedules = schedules.filter(weekday=weekday)
            for schedule in day_schedules:

                if schedule.id not in occupied_slots.get(current_date, []):
                    available_slots[current_date.isoformat()].append(schedule.id)

        return dict(available_slots)

    def get_photo(self, obj):
        if obj.base_user.photo and obj.base_user.photo.image:
            return obj.base_user.photo.pk
        return None

    def get_user_type(self, obj):
        return 'studio'

    class Meta:
        model = Photographer
        fields = '__all__'


class RegularUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'last_name', 'first_name', 'email', 'phone_number', 'photo', 'user_type', 'is_staff')
