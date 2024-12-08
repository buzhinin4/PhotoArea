from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.core.exceptions import ValidationError
from apps.schedule.models import Schedule
from apps.users.models import Studio, Photographer


class ScheduleSerializer(serializers.ModelSerializer):
    # studio = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = '__all__'

    # def get_studio(self, obj):
    #     studio = Studio.objects.filter(base_user=obj.executor).first()
    #     return studio.name


class CreateScheduleSerializer(serializers.ModelSerializer):
    executor = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Schedule
        fields = ['executor', 'weekday', 'start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        super(CreateScheduleSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request', None)
        if request and request.user.is_superuser:
            self.fields['executor'].required = True

    def validate(self, data):
        if self.instance is None:
            return self.validate_create(data)
        else:
            return self.validate_update(data)

    def validate_create(self, data):
        request = self.context.get('request')
        user = request.user

        executor = data.get('executor', None)

        if hasattr(user, 'studio_profile') or hasattr(user, 'photographer_profile'):
            if executor is not None and executor != user:
                raise serializers.ValidationError({'executor': 'Вы не можете создавать расписания для другого исполнителя.'})
            data['executor'] = user
        elif user.is_superuser:
            if executor is None:
                raise serializers.ValidationError({'executor': 'Это поле обязательно для администраторов.'})
            if not (hasattr(executor, 'studio_profile') or hasattr(executor, 'photographer_profile')):
                raise serializers.ValidationError({'executor': 'Исполнитель должен быть студией или фотографом.'})
        else:
            raise serializers.ValidationError({'executor': 'У вас нет разрешения на создание расписаний.'})

        if Schedule.objects.filter(
            executor=data['executor'],
            weekday=data['weekday'],
            start_time=data['start_time'],
            end_time=data['end_time']
        ).exists():
            raise serializers.ValidationError({'error': 'Это расписание уже существует для данного исполнителя.'})

        return data

    def validate_update(self, data):
        request = self.context.get('request')
        user = request.user
        instance = self.instance

        executor = data.get('executor', instance.executor)

        if hasattr(user, 'studio_profile') or hasattr(user, 'photographer_profile'):
            if executor is not None and executor != user:
                raise serializers.ValidationError({'executor': 'Вы не можете назначать другого исполнителя.'})
            data['executor'] = user

        elif user.is_superuser:
            if executor is None:
                raise serializers.ValidationError({'executor': 'Это поле обязательно для администраторов.'})
            if not (hasattr(executor, 'studio_profile') or hasattr(executor, 'photographer_profile')):
                raise serializers.ValidationError({'executor': 'Исполнитель должен быть студией или фотографом.'})
        else:
            raise serializers.ValidationError({'executor': 'У вас нет разрешения на изменение расписаний.'})

        if Schedule.objects.filter(
            executor=data['executor'],
            weekday=data['weekday'],
            start_time=data['start_time'],
            end_time=data['end_time']
        ).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError({'error': 'Это расписание уже существует для данного исполнителя.'})

        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
