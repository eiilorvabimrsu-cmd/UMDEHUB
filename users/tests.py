from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .bootstrap import ensure_bootstrap_admin_user
from .models import Profile


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class UserWorkflowTests(TestCase):
    def test_practitioner_registration_creates_pending_profile_and_sends_email(self):
        response = self.client.post(
            reverse('users:register'),
            {
                'username': 'practitioner1',
                'email': 'prac@example.com',
                'role': Profile.PRACTITIONER,
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
            follow=True,
        )

        user = User.objects.get(username='practitioner1')
        self.assertEqual(user.profile.role, Profile.PRACTITIONER)
        self.assertFalse(user.profile.practitioner_approved)
        self.assertContains(response, 'Request sent. Wait for admin approval before logging in as a practitioner.')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('practitioner request received', mail.outbox[0].subject.lower())

    def test_pending_practitioner_cannot_log_in(self):
        user = User.objects.create_user(username='pendingprac', password='StrongPass123!', email='pending@example.com')
        user.profile.role = Profile.PRACTITIONER
        user.profile.practitioner_approved = False
        user.profile.save()

        response = self.client.post(
            reverse('login'),
            {'username': 'pendingprac', 'password': 'StrongPass123!', 'login_role': 'practitioner'},
        )

        self.assertContains(response, 'awaiting admin approval')

    def test_student_account_cannot_use_admin_login_role(self):
        User.objects.create_user(username='studentrole', password='StrongPass123!', email='studentrole@example.com')

        response = self.client.post(
            reverse('login'),
            {'username': 'studentrole', 'password': 'StrongPass123!', 'login_role': 'admin'},
        )

        self.assertContains(response, 'This account is not an admin account.')

    def test_practitioner_account_must_use_practitioner_login_role(self):
        user = User.objects.create_user(username='roleprac', password='StrongPass123!', email='roleprac@example.com')
        user.profile.role = Profile.PRACTITIONER
        user.profile.practitioner_approved = True
        user.profile.save()

        response = self.client.post(
            reverse('login'),
            {'username': 'roleprac', 'password': 'StrongPass123!', 'login_role': 'student'},
        )

        self.assertContains(response, 'Practitioner accounts must use the Practitioner role.')

    def test_approved_practitioner_redirects_to_practitioner_dashboard(self):
        user = User.objects.create_user(username='approvedprac', password='StrongPass123!', email='approved@example.com')
        user.profile.role = Profile.PRACTITIONER
        user.profile.practitioner_approved = True
        user.profile.save()

        response = self.client.post(
            reverse('login'),
            {'username': 'approvedprac', 'password': 'StrongPass123!', 'login_role': 'practitioner'},
        )

        self.assertRedirects(response, reverse('case_studies:practitioner_dashboard'))

    def test_register_form_rejects_admin_role_selection(self):
        response = self.client.post(
            reverse('users:register'),
            {
                'username': 'newadmin',
                'email': 'newadmin@example.com',
                'role': 'admin',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
        )

        self.assertContains(response, 'Admin accounts are created by site administrators.')

    def test_bootstrap_admin_is_disabled_by_default(self):
        with patch.dict('os.environ', {}, clear=True):
            self.assertIsNone(ensure_bootstrap_admin_user())

    def test_admin_approval_view_sends_practitioner_email(self):
        admin_user = User.objects.create_superuser('admintrial', 'admin@example.com', 'StrongPass123!')
        practitioner = User.objects.create_user('reviewme', 'reviewme@example.com', 'StrongPass123!')
        practitioner.profile.role = Profile.PRACTITIONER
        practitioner.profile.practitioner_approved = False
        practitioner.profile.save()
        self.client.force_login(admin_user)

        response = self.client.get(reverse('admin:users_profile_practitioner_approve', args=[practitioner.profile.id]))

        practitioner.profile.refresh_from_db()
        self.assertRedirects(response, reverse('admin:users_profile_practitioner_requests'))
        self.assertTrue(practitioner.profile.practitioner_approved)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('approved', mail.outbox[0].subject.lower())
