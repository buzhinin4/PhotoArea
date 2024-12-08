from django.contrib.auth import get_user_model
from django.db import models

from apps.photo.models import Photo


class New(models.Model):
    title = models.CharField(max_length=100, blank=False, null=False)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    photo = models.OneToOneField(Photo, on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
