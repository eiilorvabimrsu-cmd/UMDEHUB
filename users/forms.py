from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Profile


class UserRegistrationForm(UserCreationForm):
    ADMIN = 'admin'
    ROLE_CHOICES = Profile.ROLE_CHOICES + [(ADMIN, 'Admin')]

    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')

    def clean_role(self):
        role = self.cleaned_data['role']
        if role == self.ADMIN:
            raise ValidationError('Admin accounts are created by site administrators. Use Login if you already have one.')
        return role


class RoleAwareAuthenticationForm(AuthenticationForm):
    login_role = forms.ChoiceField(
        choices=[
            (Profile.STUDENT, 'Student'),
            (Profile.PRACTITIONER, 'Practitioner'),
            ('admin', 'Admin'),
        ]
    )

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        profile = getattr(user, 'profile', None)
        selected_role = self.cleaned_data.get('login_role')

        if selected_role == 'admin' and not user.is_staff:
            raise ValidationError(
                'This account is not an admin account. Choose Student or Practitioner instead.',
                code='invalid_admin_role',
            )

        if selected_role == Profile.PRACTITIONER and (not profile or not profile.is_practitioner):
            raise ValidationError(
                'This account is not registered as a practitioner.',
                code='invalid_practitioner_role',
            )

        if selected_role == Profile.STUDENT and user.is_staff:
            raise ValidationError(
                'Admin accounts must use the Admin role.',
                code='invalid_student_role',
            )

        if selected_role == Profile.STUDENT and profile and profile.is_practitioner and not user.is_staff:
            raise ValidationError(
                'Practitioner accounts must use the Practitioner role.',
                code='invalid_student_practitioner_role',
            )

        if profile and profile.is_practitioner and not profile.practitioner_approved and not user.is_staff:
            raise ValidationError(
                'Your practitioner account is awaiting admin approval.',
                code='practitioner_pending',
            )


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('full_name', 'institution', 'year_of_study', 'bio')
        widgets = {'bio': forms.Textarea(attrs={'rows': 4})}
