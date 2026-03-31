from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'practitioner_approved', 'institution', 'year_of_study')
    list_filter = ('role', 'practitioner_approved')
    search_fields = ('user__username', 'full_name', 'institution')
