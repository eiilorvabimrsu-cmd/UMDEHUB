from django.contrib import admin

from .models import AnswerRecord, Choice, Question, Result


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'subject', 'topic', 'difficulty')
    list_filter = ('subject', 'topic', 'difficulty')
    search_fields = ('text', 'topic__title', 'subject__name')
    inlines = [ChoiceInline]


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz_type', 'score', 'total_questions', 'percentage', 'date')
    list_filter = ('quiz_type', 'subject', 'topic')
    search_fields = ('user__username',)


@admin.register(AnswerRecord)
class AnswerRecordAdmin(admin.ModelAdmin):
    list_display = ('result', 'question', 'selected_choice', 'is_correct')
    list_filter = ('is_correct',)
