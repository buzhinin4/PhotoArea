from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.photo.models import Photo


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    fields = ['image_image', 'image']
    readonly_fields = ['image_image']

    list_display = ['image_image', ]

    @admin.display(description="Photo")
    def image_image(self, photo: Photo):
        if photo.image:
            return mark_safe(f"<img src='{photo.image.url}' width=50 />")
        return "Without photo"