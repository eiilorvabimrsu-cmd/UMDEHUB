from django.urls import path

from .views import profile_view, register_view

app_name = 'users'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
]
