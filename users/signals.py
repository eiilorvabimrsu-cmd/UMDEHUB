import os

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_migrate)
def ensure_bootstrap_admin(sender, **kwargs):
    username = os.environ.get('BOOTSTRAP_ADMIN_USERNAME')
    password = os.environ.get('BOOTSTRAP_ADMIN_PASSWORD')
    email = os.environ.get('BOOTSTRAP_ADMIN_EMAIL', 'admin@example.com')

    if not username or not password:
        return

    user, _ = User.objects.get_or_create(
        username=username,
        defaults={'email': email, 'is_staff': True, 'is_superuser': True},
    )
    user.email = user.email or email
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
