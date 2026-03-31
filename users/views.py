from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import ProfileForm, UserProfileForm, UserRegistrationForm


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_staff:
            return reverse_lazy('admin:index')
        return reverse_lazy('dashboard:overview')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_role'] = self.request.GET.get('role', 'student')
        return context


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:overview')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to the Dental Learning Platform.')
            return redirect('dashboard:overview')
    else:
        form = UserRegistrationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was updated successfully.')
            return redirect('users:profile')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    return render(
        request,
        'users/profile.html',
        {'user_form': user_form, 'profile_form': profile_form},
    )
