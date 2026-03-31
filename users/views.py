from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .bootstrap import ensure_bootstrap_admin_user
from .forms import (
    ProfileForm,
    RoleAwareAuthenticationForm,
    UserProfileForm,
    UserRegistrationForm,
)


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = RoleAwareAuthenticationForm

    def dispatch(self, request, *args, **kwargs):
        ensure_bootstrap_admin_user()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        user = self.request.user
        if user.is_staff:
            return reverse_lazy('admin:index')
        if getattr(user, 'profile', None) and user.profile.is_practitioner:
            return reverse_lazy('case_studies:practitioner_dashboard')
        return reverse_lazy('dashboard:overview')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_role'] = self.request.GET.get('role', 'student')
        return context


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:overview')

    initial_role = request.GET.get('role')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = user.profile
            selected_role = form.cleaned_data['role']
            profile.role = selected_role
            profile.practitioner_approved = selected_role == profile.STUDENT
            profile.save()

            if selected_role == profile.PRACTITIONER:
                messages.success(
                    request,
                    'Your practitioner account request was submitted. An admin must approve it before you can log in.',
                )
                return redirect('login')

            login(request, user)
            messages.success(request, 'Welcome to UMOL\'S DENTAL HUB.')
            return redirect('dashboard:overview')
    else:
        form = UserRegistrationForm(initial={'role': initial_role} if initial_role else None)

    return render(request, 'users/register.html', {'form': form, 'selected_role': initial_role or 'student'})


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
