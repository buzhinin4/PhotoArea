from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.core.exceptions import ValidationError
from apps.order.models import Order
from apps.schedule.models import Schedule
from django.utils.timezone import datetime


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class CreateOrderSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Order
        fields = ['executor', 'client', 'schedule', 'date']

    def __init__(self, *args, **kwargs):
        super(CreateOrderSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request', None)
        if request and request.user.is_superuser:
            self.fields['client'].required = True

    def validate(self, data):
        if self.instance is None:
            return self.validate_create(data)
        else:
            return self.validate_update(data)

    def validate_create(self, data):
        request = self.context.get('request')
        current_user = request.user

        client = data.get('client', None)
        executor = data.get('executor', None)
        schedule = data.get('schedule', None)
        date = data.get('date', None)

        if hasattr(client, 'studio_profile'):
            raise ValidationError({'client': 'Studio cannot create orders'})

        if client is None:
            client = current_user
            data['client'] = client

        if client != current_user and not current_user.is_superuser:
            raise ValidationError({'client': 'You cannot create orders for another client'})

        if not (hasattr(executor, 'studio_profile') or hasattr(executor, 'photographer_profile')):
            raise ValidationError({'executor': 'Executor must be studio or photographer'})

        if not self.is_date_matching_schedule(date, schedule):
            raise ValidationError({'date': 'The selected date does not match the weekday of the schedule'})

        if not self.is_exec_matching_schedule(executor, schedule):
            raise ValidationError({'Executor': 'The selected executor does not match the executor of the schedule'})

        overlapping_orders = Order.objects.filter(schedule=schedule, date=date)

        if overlapping_orders.exists():
            raise ValidationError("This schedule slot is already booked for the selected date.")

        return data

    def validate_update(self, data):
        request = self.context.get('request')
        current_user = request.user
        instance = self.instance
        current_client = instance.client

        client = data.get('client', None)
        executor = data.get('executor', instance.executor)
        schedule = data.get('schedule', instance.schedule)
        date = data.get('date', instance.date)

        if hasattr(client, 'studio_profile'):
            raise ValidationError({'client': 'Студия не может создавать заказы.'})

        if client is None:
            client = current_user
            data['client'] = client

        if client != current_client and not current_user.is_superuser:
            raise ValidationError({'client': 'Вы не можете изменять заказы для другого клиента.'})

        if not (hasattr(executor, 'studio_profile') or hasattr(executor, 'photographer_profile')):
            raise ValidationError({'executor': 'Исполнитель должен быть студией или фотографом.'})

        if not self.is_date_matching_schedule(date, schedule):
            raise ValidationError({'date': 'Выбранная дата не соответствует дню недели расписания.'})

        overlapping_orders = Order.objects.filter(
            schedule=schedule,
            date=date
        ).exclude(pk=instance.pk)

        if overlapping_orders.exists():
            raise ValidationError("Этот временной слот уже занят на выбранную дату.")

        return data

    def is_date_matching_schedule(self, date, schedule):
        if date and schedule:
            date_weekday = date.weekday() + 1
            return date_weekday == schedule.weekday
        return False

    def is_exec_matching_schedule(self, executor, schedule):
        if executor and schedule:
            return executor == schedule.executor
        return False

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
