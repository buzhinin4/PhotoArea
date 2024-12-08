from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError


class Schedule(models.Model):
    DAYS_OF_WEEK = (
        (1, "Monday"),
        (2, "Tuesday"),
        (3, "Wednesday"),
        (4, "Thursday"),
        (5, "Friday"),
        (6, "Saturday"),
        (7, "Sunday"),
    )

    executor = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    weekday = models.PositiveSmallIntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField(blank=False, null=False)
    end_time = models.TimeField(blank=False, null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['executor', 'weekday', 'start_time', 'end_time'],
                name='unique_schedule_per_executor'
            )
        ]
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"
        ordering = ['executor', 'weekday', 'start_time']

    def __str__(self):
        day = dict(self.DAYS_OF_WEEK).get(self.weekday, "Unknown Day")
        return f"{self.executor} - {day}: {self.start_time} - {self.end_time}"

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be earlier than end time.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
