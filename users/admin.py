from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'practitioner_approved', 'institution', 'year_of_study')
    list_filter = ('role', 'practitioner_approved')
    search_fields = ('user__username', 'full_name', 'institution')
    actions = ['approve_practitioners', 'dismiss_practitioners']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'practitioner-requests/',
                self.admin_site.admin_view(self.practitioner_requests_view),
                name='users_profile_practitioner_requests',
            ),
            path(
                'practitioner-requests/<int:profile_id>/approve/',
                self.admin_site.admin_view(self.approve_request_view),
                name='users_profile_practitioner_approve',
            ),
            path(
                'practitioner-requests/<int:profile_id>/dismiss/',
                self.admin_site.admin_view(self.dismiss_request_view),
                name='users_profile_practitioner_dismiss',
            ),
        ]
        return custom_urls + urls

    def practitioner_requests_view(self, request):
        pending_profiles = Profile.objects.select_related('user').filter(
            role=Profile.PRACTITIONER,
            practitioner_approved=False,
        )
        context = self.admin_site.each_context(request)
        context.update({
            'opts': self.model._meta,
            'title': 'Practitioner Account Requests',
            'pending_profiles': pending_profiles,
        })
        return TemplateResponse(request, 'admin/users/profile/practitioner_requests.html', context)

    def approve_request_view(self, request, profile_id):
        profile = self.get_object(request, profile_id)
        if profile and profile.role == Profile.PRACTITIONER:
            profile.practitioner_approved = True
            profile.save(update_fields=['practitioner_approved'])
            self.message_user(
                request,
                f'Practitioner account approved for {profile.user.username}.',
                level=messages.SUCCESS,
            )
        return HttpResponseRedirect(reverse('admin:users_profile_practitioner_requests'))

    def dismiss_request_view(self, request, profile_id):
        profile = self.get_object(request, profile_id)
        if profile and profile.role == Profile.PRACTITIONER:
            profile.role = Profile.STUDENT
            profile.practitioner_approved = False
            profile.save(update_fields=['role', 'practitioner_approved'])
            self.message_user(
                request,
                f'Practitioner request dismissed for {profile.user.username}. The account remains a student account.',
                level=messages.WARNING,
            )
        return HttpResponseRedirect(reverse('admin:users_profile_practitioner_requests'))

    @admin.action(description='Approve selected practitioner requests')
    def approve_practitioners(self, request, queryset):
        updated = queryset.filter(role=Profile.PRACTITIONER).update(practitioner_approved=True)
        self.message_user(request, f'{updated} practitioner request(s) approved.', level=messages.SUCCESS)

    @admin.action(description='Dismiss selected practitioner requests')
    def dismiss_practitioners(self, request, queryset):
        updated = queryset.filter(role=Profile.PRACTITIONER).update(
            role=Profile.STUDENT,
            practitioner_approved=False,
        )
        self.message_user(request, f'{updated} practitioner request(s) dismissed.', level=messages.WARNING)
