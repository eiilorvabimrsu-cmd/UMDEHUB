from django.db import models
from django.urls import reverse


class Subject(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('notes:subject_topics', args=[self.pk])


class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=150)
    overview = models.TextField(blank=True)

    class Meta:
        ordering = ['subject__name', 'title']
        unique_together = ('subject', 'title')

    def __str__(self):
        return f'{self.subject.name} - {self.title}'

    def get_absolute_url(self):
        return reverse('notes:topic_notes', args=[self.pk])


class Note(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=150, default='Study Note')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f'{self.topic.title} - {self.title}'
