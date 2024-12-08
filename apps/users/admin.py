from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from .models import User, Studio, Photographer
from ..order.models import Order
from ..schedule.models import Schedule


class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'user_photo', 'photo', 'date_birth')
    search_fields = ('username', 'email')
    readonly_fields = ('user_photo', 'date_joined', 'last_login')
    ordering = ('email',)

    @admin.display(description="Photo")
    def user_photo(self, user: User):
        if user.photo:
            return mark_safe(f"<img src='{user.photo.image.url}' width=50 />")
        return "Without photo"

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'photo', 'user_photo', 'date_birth')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(User, CustomUserAdmin)


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_user', 'address')
    search_fields = ('name', 'base_user__email', 'address__street')
    readonly_fields = ('display_schedules', 'display_orders')

    def display_schedules(self, obj):
        schedules = Schedule.objects.filter(executor=obj.base_user)
        if schedules.exists():
            return format_html(
                "<ul>{}</ul>",
                format_html_join(
                    "\n",
                    "<li>{} {} - {}</li>",
                    ((s.pk, s.get_weekday_display(), s.start_time, s.end_time) for s in schedules)
                )
            )
        return "No schedules available"

    display_schedules.short_description = "Schedules"

    def display_orders(self, obj):
        orders = Order.objects.filter(executor=obj.base_user)
        if orders.exists():
            return format_html(
                "<ul>{}</ul>",
                format_html_join(
                    "\n",
                    "<li>Client: {} | Date: {} | Schedule: {} {} - {}</li>",
                    (
                        (
                            order.client.email if order.client else "Unknown",
                            order.date,
                            order.schedule.get_weekday_display(),
                            order.schedule.start_time,
                            order.schedule.end_time,
                        )
                        for order in orders
                    )
                )
            )
        return "No orders available"

    display_orders.short_description = "Orders"


@admin.register(Photographer)
class PhotographerAdmin(admin.ModelAdmin):
    list_display = ('base_user', 'description')
    search_fields = ('base_user__email', 'base_user__username')
    readonly_fields = ('display_schedules', 'display_orders')

    def display_schedules(self, obj):
        schedules = Schedule.objects.filter(executor=obj.base_user)
        if schedules.exists():
            return format_html(
                "<ul>{}</ul>",
                format_html_join(
                    "\n",
                    "<li>{} {} - {}</li>",
                    ((s.pk, s.get_weekday_display(), s.start_time, s.end_time) for s in schedules)
                )
            )
        return "No schedules available"

    display_schedules.short_description = "Schedules"

    def display_orders(self, obj):
        orders = Order.objects.filter(executor=obj.base_user)
        if orders.exists():
            return format_html(
                "<ul>{}</ul>",
                format_html_join(
                    "\n",
                    "<li>Client: {} | Date: {} | Schedule: {} {} - {}</li>",
                    (
                        (
                            order.client.email if order.client else "Unknown",
                            order.date,
                            order.schedule.get_weekday_display(),
                            order.schedule.start_time,
                            order.schedule.end_time,
                        )
                        for order in orders
                    )
                )
            )
        return "No orders available"

    display_orders.short_description = "Orders"

