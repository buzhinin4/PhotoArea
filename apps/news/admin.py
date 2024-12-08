from django.contrib import admin
from django.utils.html import format_html

from apps.news.models import New
from .forms import NewAdminForm


@admin.register(New)
class NewAdmin(admin.ModelAdmin):
    form = NewAdminForm  # Используйте вашу пользовательскую форму
    list_display = ('title', 'author', 'created_at', 'display_photo')
    readonly_fields = ('display_photo',)

    fieldsets = (
        (None, {
            'fields': ('title', 'text', 'author', 'photo_upload', 'existing_photo')
        }),
        ('Photo', {
            'fields': ('display_photo',),
        }),
    )

    def display_photo(self, obj):
        if obj.photo and obj.photo.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.photo.image.url)
        return "No Photo"

    display_photo.short_description = 'Current Photo'
