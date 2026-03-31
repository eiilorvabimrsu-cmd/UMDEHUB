from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'year_of_study')
    search_fields = ('user__username', 'full_name', 'institution')
