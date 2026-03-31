from django.contrib import admin

from .models import PastPaper


@admin.register(PastPaper)
class PastPaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'year')
    list_filter = ('subject', 'year')
    search_fields = ('title', 'subject__name')
