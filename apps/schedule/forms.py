from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import Schedule


class ScheduleAdminForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['executor'].queryset = get_user_model().objects.filter(
            studio_profile__isnull=False
        ) | get_user_model().objects.filter(
            photographer_profile__isnull=False
        )

    def clean(self):
        cleaned_data = super().clean()
        user = self.current_user

        executor = cleaned_data.get('executor')

        if hasattr(user, 'studio_profile') or hasattr(user, 'photographer_profile'):
            cleaned_data['executor'] = user

        elif user.is_superuser:
            if not executor:
                raise ValidationError({"executor": "This field is required for admin users."})

        else:
            raise ValidationError("You do not have permission to perform this action.")

        return cleaned_data
