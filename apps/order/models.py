from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError
from apps.schedule.models import Schedule


class Order(models.Model):
    executor = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='executor'
    )
    client = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='client',
        null=True,
        blank=True
    )
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        related_name='schedule'
    )
    date = models.DateField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['executor', 'client', 'schedule', 'date'],
                name='unique_booking_per_schedule'
            )
        ]

    def clean(self):
        super().clean()
        overlapping_orders = Order.objects.filter(
            schedule=self.schedule,
            date=self.date
        ).exclude(id=self.id)

        if overlapping_orders.exists():
            raise ValidationError("This schedule slot is already booked for the selected date.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
