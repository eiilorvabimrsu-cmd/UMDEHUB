from django.contrib import admin

from .models import Note, Subject, Topic


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 1


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [TopicInline]


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject')
    list_filter = ('subject',)
    search_fields = ('title', 'subject__name')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'updated_at')
    list_filter = ('topic__subject', 'topic')
    search_fields = ('title', 'topic__title', 'topic__subject__name')
