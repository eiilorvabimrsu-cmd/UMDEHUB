from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse

from .models import Contribution, ImportedChoice, ImportedQuestion, QuestionImportBatch, StudyVideo


class ImportedChoiceInline(admin.TabularInline):
    model = ImportedChoice
    extra = 0


class ImportedQuestionInline(admin.TabularInline):
    model = ImportedQuestion
    extra = 0
    show_change_link = True


@admin.register(QuestionImportBatch)
class QuestionImportBatchAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'topic', 'status', 'scanned_detected', 'review_link')
    list_filter = ('status', 'subject', 'scanned_detected')
    search_fields = ('title', 'subject__name', 'topic__title')
    inlines = [ImportedQuestionInline]

    def review_link(self, obj):
        url = reverse('contributions:import_review', args=[obj.pk])
        return format_html('<a href="{}">Open review</a>', url)


@admin.register(ImportedQuestion)
class ImportedQuestionAdmin(admin.ModelAdmin):
    list_display = ('batch', 'order', 'text', 'detected_answer_label')
    inlines = [ImportedChoiceInline]


@admin.register(StudyVideo)
class StudyVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'topic', 'submitted_by')
    list_filter = ('subject', 'topic')
    search_fields = ('title', 'subject__name', 'topic__title')


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('title', 'contribution_type', 'user', 'status', 'subject', 'topic', 'created_at')
    list_filter = ('contribution_type', 'status', 'subject')
    search_fields = ('title', 'user__username', 'subject__name', 'topic__title')
    actions = ['approve_selected', 'reject_selected']

    @admin.action(description='Approve selected contributions')
    def approve_selected(self, request, queryset):
        approved = 0
        for contribution in queryset.filter(status=Contribution.PENDING):
            contribution.approve(request.user)
            approved += 1
        self.message_user(request, f'{approved} contributions approved.', level=messages.SUCCESS)

    @admin.action(description='Reject selected contributions')
    def reject_selected(self, request, queryset):
        rejected = 0
        for contribution in queryset.filter(status=Contribution.PENDING):
            contribution.reject(request.user)
            rejected += 1
        self.message_user(request, f'{rejected} contributions rejected.', level=messages.WARNING)
