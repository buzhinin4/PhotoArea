from django.contrib import admin
from .models import Portfolio, PortfolioPhotos, Photo


class PortfolioPhotosInline(admin.TabularInline):
    model = PortfolioPhotos
    extra = 1
    verbose_name = "Связанная фотография"
    verbose_name_plural = "Связанные фотографии"


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_owner', 'description', 'photo_count')
    search_fields = ('description', 'studio__name', 'photographer__base_user__username')
    list_filter = ('studio', 'photographer')
    inlines = [PortfolioPhotosInline]

    def get_owner(self, obj):
        if obj.studio:
            return f"Studio: {obj.studio.name}"
        elif obj.photographer:
            return f"Photographer: {obj.photographer.base_user.username}"
        return "No owner"
    get_owner.short_description = "Owner"

    def photo_count(self, obj):
        return obj.photos.count()
    photo_count.short_description = "Number of Photos"
