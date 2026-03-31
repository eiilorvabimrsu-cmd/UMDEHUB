from django.conf import settings
from django.db import models


class Profile(models.Model):
    STUDENT = 'student'
    PRACTITIONER = 'practitioner'
    ROLE_CHOICES = [
        (STUDENT, 'Student'),
        (PRACTITIONER, 'Practitioner'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=120, blank=True)
    institution = models.CharField(max_length=150, blank=True)
    year_of_study = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)
    practitioner_approved = models.BooleanField(default=False)

    def __str__(self):
        return f'Profile for {self.user.username}'

    @property
    def is_practitioner(self):
        return self.role == self.PRACTITIONER

    @property
    def is_student(self):
        return self.role == self.STUDENT
