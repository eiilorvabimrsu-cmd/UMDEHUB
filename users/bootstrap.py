import os

from django.contrib.auth.models import User


def ensure_bootstrap_admin_user():
    username = os.environ.get('BOOTSTRAP_ADMIN_USERNAME')
    password = os.environ.get('BOOTSTRAP_ADMIN_PASSWORD')
    email = os.environ.get('BOOTSTRAP_ADMIN_EMAIL', 'admin@example.com')

    if not username or not password:
        return None

    user, _ = User.objects.get_or_create(
        username=username,
        defaults={'email': email, 'is_staff': True, 'is_superuser': True},
    )
    user.email = user.email or email
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
    return user
