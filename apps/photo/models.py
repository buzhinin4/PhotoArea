from django.db import models
from django.utils import timezone
from social_core.utils import slugify


def get_upload_path(instance, filename):
    now = timezone.now()
    base_dir = 'photos'
    date_path = now.strftime("%Y/%m/%d")

    if hasattr(instance, 'new_info'):
        username = instance.new_info['author']
        title = instance.new_info['title']
        return f'{base_dir}/News_Photo/user_photos/{username}/{title}/{filename}'
    if hasattr(instance, 'user_info'):
        username = instance.user_info['username']
        return f'{base_dir}/Avatars/user_photos/{username}/{filename}'
    if hasattr(instance, 'portfolio_info'):
        username = instance.portfolio_info['username']
        portfolio_id = instance.portfolio_info['portfolio_id']
        return f'{base_dir}/Portfolio_Photo/{username}/{portfolio_id}/{filename}'
    else:
        slug_title = slugify('c')
        return f'{base_dir}/new_photos/{slug_title}/{filename}'
    return f'{base_dir}/other_photos/{date_path}/{filename}'


class Photo(models.Model):
    image = models.ImageField(upload_to=get_upload_path, help_text="photo")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo {self.id}"
