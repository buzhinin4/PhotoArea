from django.contrib.auth import get_user_model
from django.db import models


class Comment(models.Model):
    class Rate(models.IntegerChoices):
        ONE = 1, '1'
        TWO = 2, '2'
        THREE = 3, '3'
        FOUR = 4, '4'
        FIVE = 5, '5'

    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    destination = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='comments')

    rate = models.IntegerField(choices=Rate.choices, default=Rate.ONE)
    title = models.CharField(blank=True, max_length=80)
    body = models.TextField(blank=True)

    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Created")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Updated")

    class Meta:
        ordering = ['-time_create']

    def __str__(self):
        return f'Comment by {self.author} on {self.time_create}. Rate: {self.rate}'
