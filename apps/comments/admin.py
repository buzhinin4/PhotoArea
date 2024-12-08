from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Comment


class CommentAdmin(admin.ModelAdmin):
    fields = ['author', 'destination', 'title', 'rate']
    list_display = ['id', 'author', 'destination', 'title', 'rate']
    search_fields = ['author', 'destination', 'title']


admin.site.register(Comment, CommentAdmin)
