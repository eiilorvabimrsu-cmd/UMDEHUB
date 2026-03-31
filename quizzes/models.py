from django.conf import settings
from django.db import models

from notes.models import Subject, Topic


class Question(models.Model):
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    DIFFICULTY_CHOICES = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
    ]

    text = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default=BEGINNER)
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['subject__name', 'topic__title', 'id']

    def __str__(self):
        return f'{self.topic.title}: {self.text[:60]}'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Result(models.Model):
    TOPIC = 'topic'
    RANDOM = 'random'
    MOCK = 'mock'
    QUIZ_TYPE_CHOICES = [
        (TOPIC, 'Topic Quiz'),
        (RANDOM, 'Random Quiz'),
        (MOCK, 'Mock Exam'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='results')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, related_name='results', null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, related_name='results', null=True, blank=True)
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPE_CHOICES, default=TOPIC)
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.user.username} - {self.score}/{self.total_questions}'


class AnswerRecord(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='answer_records',
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        unique_together = ('result', 'question')

    def __str__(self):
        return f'{self.result.user.username} - {self.question_id}'
