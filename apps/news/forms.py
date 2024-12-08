# apps/news/forms.py

from django import forms
from .models import New, Photo


class NewAdminForm(forms.ModelForm):
    photo_upload = forms.ImageField(required=False, label="Загрузить новую фотографию")
    existing_photo = forms.ModelChoiceField(
        queryset=Photo.objects.all(),
        required=False,
        label="Выбрать существующую фотографию"
    )

    class Meta:
        model = New
        fields = ['title', 'text', 'author', 'photo_upload', 'existing_photo']

    def clean(self):
        cleaned_data = super().clean()
        photo_upload = cleaned_data.get('photo_upload')
        existing_photo = cleaned_data.get('existing_photo')

        if not photo_upload and not existing_photo:
            raise forms.ValidationError("Необходимо загрузить новую фотографию или выбрать существующую.")

        if photo_upload and existing_photo:
            raise forms.ValidationError(
                "Выберите либо загрузить новую фотографию, либо выбрать существующую, но не оба варианта одновременно.")

        return cleaned_data

    def save(self, commit=True):
        new_instance = super(NewAdminForm, self).save(commit=False)
        photo_upload = self.cleaned_data.get('photo_upload')
        existing_photo = self.cleaned_data.get('existing_photo')

        if not commit:
            new_instance.save()
            if photo_upload:
                if new_instance.photo:
                    new_instance.photo.delete()
                    photo = Photo(image=photo_upload)
                    photo.new_info = {'author': new_instance.author, 'title': new_instance.title}
                    photo.save()
                    new_instance.photo = photo
                    new_instance.save()
                else:
                    # photo = Photo(image=photo_upload)
                    # photo.new_title = self.cleaned_data.get('title')
                    # photo.save()
                    # new_instance.photo = photo
                    # new_instance.save()

                    photo = Photo(image=photo_upload)
                    photo.new_info = {'author': new_instance.author, 'title': new_instance.title}
                    photo.save()
                    new_instance.photo = photo
                    new_instance.save()
            elif existing_photo:
                new_instance.photo = existing_photo
                new_instance.save()

        return new_instance
