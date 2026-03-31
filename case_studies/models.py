from django.conf import settings
from django.db import models


class CaseStudy(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    FLAGGED = 'flagged'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (FLAGGED, 'Flagged'),
    ]

    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (OTHER, 'Other'),
    ]

    title = models.CharField(max_length=200)
    practitioner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='case_studies',
    )
    patient_age = models.PositiveIntegerField()
    patient_gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    chief_complaint = models.TextField()
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    management_steps = models.TextField()
    discussion = models.TextField()
    is_anonymized = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    admin_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CaseMedia(models.Model):
    IMAGE = 'image'
    VIDEO = 'video'
    XRAY = 'xray'
    DOCUMENT = 'document'
    MEDIA_TYPE_CHOICES = [
        (IMAGE, 'Image'),
        (VIDEO, 'Video'),
        (XRAY, 'X-ray'),
        (DOCUMENT, 'Document'),
    ]

    case = models.ForeignKey(CaseStudy, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='case_media/')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)

    def __str__(self):
        return f'{self.case.title} - {self.media_type}'
