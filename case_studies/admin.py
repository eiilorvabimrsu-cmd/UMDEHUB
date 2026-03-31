from django.contrib import admin, messages

from .models import CaseMedia, CaseStudy


class CaseMediaInline(admin.TabularInline):
    model = CaseMedia
    extra = 1


@admin.register(CaseStudy)
class CaseStudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'practitioner', 'status', 'patient_age', 'patient_gender', 'created_at')
    list_filter = ('status', 'patient_gender', 'is_anonymized')
    search_fields = ('title', 'practitioner__username', 'diagnosis')
    inlines = [CaseMediaInline]
    actions = ['approve_cases', 'reject_cases', 'flag_cases']

    @admin.action(description='Approve selected cases')
    def approve_cases(self, request, queryset):
        updated = queryset.update(status=CaseStudy.APPROVED)
        self.message_user(request, f'{updated} case studies approved.', level=messages.SUCCESS)

    @admin.action(description='Reject selected cases')
    def reject_cases(self, request, queryset):
        updated = queryset.update(status=CaseStudy.REJECTED)
        self.message_user(request, f'{updated} case studies rejected.', level=messages.WARNING)

    @admin.action(description='Flag selected cases')
    def flag_cases(self, request, queryset):
        updated = queryset.update(status=CaseStudy.FLAGGED)
        self.message_user(request, f'{updated} case studies flagged.', level=messages.WARNING)
