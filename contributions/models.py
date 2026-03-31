from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone

from notes.models import Note, Subject, Topic
from papers.models import PastPaper
from quizzes.models import Choice, Question


class StudyVideo(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='study_videos')
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='study_videos',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200)
    youtube_url = models.URLField()
    description = models.TextField(blank=True)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_videos',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class QuestionImportBatch(models.Model):
    DOCX = 'docx'
    PDF = 'pdf'
    SOURCE_CHOICES = [(DOCX, 'Word Document'), (PDF, 'PDF Document')]

    PENDING = 'pending'
    SCANNED_ONLY = 'scanned_only'
    READY = 'ready'
    PUBLISHED = 'published'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SCANNED_ONLY, 'Scanned PDF detected'),
        (READY, 'Ready for review'),
        (PUBLISHED, 'Published'),
    ]

    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='question_imports')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='question_imports')
    source_file = models.FileField(upload_to='question_imports/')
    source_type = models.CharField(max_length=10, choices=SOURCE_CHOICES)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='question_imports',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    scanned_detected = models.BooleanField(default=False)
    extracted_text = models.TextField(blank=True)
    parser_notes = models.TextField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ImportedQuestion(models.Model):
    batch = models.ForeignKey(QuestionImportBatch, on_delete=models.CASCADE, related_name='questions')
    order = models.PositiveIntegerField()
    text = models.TextField()
    explanation = models.TextField(blank=True)
    detected_answer_label = models.CharField(max_length=1, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.batch.title} - Q{self.order}'


class ImportedChoice(models.Model):
    question = models.ForeignKey(ImportedQuestion, on_delete=models.CASCADE, related_name='choices')
    label = models.CharField(max_length=1)
    text = models.CharField(max_length=255)
    is_selected_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ['label']

    def __str__(self):
        return f'{self.question} - {self.label}'


class Contribution(models.Model):
    NOTE = 'note'
    VIDEO = 'video'
    TOPIC = 'topic'
    PAPER = 'paper'
    TYPE_CHOICES = [
        (NOTE, 'Study note'),
        (VIDEO, 'Study video'),
        (TOPIC, 'Topic suggestion'),
        (PAPER, 'Past paper'),
    ]

    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contributions')
    contribution_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    source_file = models.FileField(upload_to='contributions/notes/', blank=True)
    youtube_url = models.URLField(blank=True)
    paper_file = models.FileField(upload_to='contributions/papers/', blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    admin_feedback = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_contributions',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_contribution_type_display()} - {self.title}'

    def approve(self, reviewer):
        if self.status == self.APPROVED:
            return

        if self.contribution_type == self.NOTE and self.topic:
            note_content = self.content
            if self.source_file and not note_content:
                extension = self.source_file.name.rsplit('.', 1)[-1].lower()
                from .utils import extract_text_from_docx, extract_text_from_pdf

                if extension == 'docx':
                    note_content, _, _ = extract_text_from_docx(self.source_file.path)
                elif extension == 'pdf':
                    note_content, scanned_detected, _ = extract_text_from_pdf(self.source_file.path)
                    if scanned_detected:
                        note_content = ''
            Note.objects.create(topic=self.topic, title=self.title, content=note_content)
        elif self.contribution_type == self.VIDEO and self.subject:
            StudyVideo.objects.create(
                subject=self.subject,
                topic=self.topic,
                title=self.title,
                youtube_url=self.youtube_url,
                description=self.content,
                submitted_by=self.user,
            )
        elif self.contribution_type == self.TOPIC and self.subject:
            Topic.objects.get_or_create(
                subject=self.subject,
                title=self.title,
                defaults={'overview': self.content},
            )
        elif self.contribution_type == self.PAPER and self.subject and self.paper_file:
            PastPaper.objects.create(
                title=self.title,
                year=self.year or timezone.now().year,
                file=self.paper_file,
                subject=self.subject,
            )

        self.status = self.APPROVED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'admin_feedback'])
        self.send_status_email()

    def reject(self, reviewer):
        self.status = self.REJECTED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'admin_feedback'])
        self.send_status_email()

    def send_status_email(self):
        if not self.user.email:
            return

        send_mail(
            subject=f'UMOL\'S DENTAL HUB contribution update: {self.get_status_display()}',
            message=(
                f'Hello {self.user.username},\n\n'
                f'Your {self.get_contribution_type_display().lower()} submission "{self.title}" '
                f'has been {self.get_status_display().lower()}.\n\n'
                f'Admin feedback: {self.admin_feedback or "No additional feedback was provided."}\n\n'
                'Thank you for helping improve UMOL\'S DENTAL HUB.'
            ),
            from_email=None,
            recipient_list=[self.user.email],
            fail_silently=True,
        )
