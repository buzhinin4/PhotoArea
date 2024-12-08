from django.contrib import admin
from django.contrib.auth import get_user_model

from .forms import ScheduleAdminForm
from apps.schedule.models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    fields = ['id', 'weekday', 'start_time', 'end_time', 'executor']
    readonly_fields = ['id']
    list_display = ['id', 'weekday', 'start_time', 'end_time', 'executor']
    list_display_links = ('id', )
    list_editable = ['weekday', 'executor']
    save_on_top = True

    form = ScheduleAdminForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form
