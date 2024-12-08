from django.contrib import admin

from apps.order.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('executor', 'client', 'schedule_display', 'date', 'created_at', 'updated_at')
    list_filter = ('date', 'executor', 'schedule__weekday')
    search_fields = ('executor__email', 'client__email', 'schedule__executor__email')
    readonly_fields = ('created_at', 'updated_at', 'schedule_display')
    fields = ('executor', 'client', 'schedule_display', 'date', 'created_at', 'updated_at')

    def schedule_display(self, obj):
        """
        Отображает текстовое представление расписания.
        """
        if obj.schedule:
            return f"{obj.schedule.get_weekday_display()} {obj.schedule.start_time} - {obj.schedule.end_time}"
        return "No schedule selected"
    schedule_display.short_description = "Schedule"

    def get_queryset(self, request):
        """
        Настраивает запрос для отображения связанных объектов.
        """
        qs = super().get_queryset(request)
        return qs.select_related('executor', 'client', 'schedule')

    def save_model(self, request, obj, form, change):
        """
        Кастомное сохранение для логирования изменений.
        """
        obj.save()
