from django.db import models

from notes.models import Subject


class PastPaper(models.Model):
    title = models.CharField(max_length=150)
    year = models.PositiveIntegerField()
    file = models.FileField(upload_to='past_papers/')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='past_papers')

    class Meta:
        ordering = ['-year', 'title']

    def __str__(self):
        return f'{self.title} ({self.year})'
