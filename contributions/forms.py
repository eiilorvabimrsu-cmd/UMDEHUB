from django import forms

from notes.models import Subject, Topic

from .models import Contribution, QuestionImportBatch


class QuestionImportForm(forms.ModelForm):
    class Meta:
        model = QuestionImportBatch
        fields = ('title', 'subject', 'topic', 'source_file')

    def clean_source_file(self):
        uploaded_file = self.cleaned_data['source_file']
        extension = uploaded_file.name.rsplit('.', 1)[-1].lower()
        if extension not in {'docx', 'pdf'}:
            raise forms.ValidationError('Only DOCX and PDF files are supported.')
        return uploaded_file


class NoteContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ('subject', 'topic', 'title', 'content', 'source_file')
        widgets = {'content': forms.Textarea(attrs={'rows': 8})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.contribution_type = Contribution.NOTE
        self.fields['subject'].required = True
        self.fields['topic'].required = True

    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject')
        topic = cleaned_data.get('topic')
        content = cleaned_data.get('content')
        source_file = cleaned_data.get('source_file')
        if topic and subject and topic.subject_id != subject.id:
            self.add_error('topic', 'The selected topic must belong to the selected subject.')
        if not content and not source_file:
            raise forms.ValidationError('Provide typed note content or upload a DOCX/PDF note file.')
        if source_file:
            extension = source_file.name.rsplit('.', 1)[-1].lower()
            if extension not in {'docx', 'pdf'}:
                self.add_error('source_file', 'Only DOCX and PDF note files are supported.')
        return cleaned_data


class VideoContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ('subject', 'topic', 'title', 'youtube_url', 'content')
        widgets = {'content': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Why is this video helpful?'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.contribution_type = Contribution.VIDEO
        self.fields['subject'].required = True

    def clean(self):
        cleaned_data = super().clean()
        subject = cleaned_data.get('subject')
        topic = cleaned_data.get('topic')
        if topic and subject and topic.subject_id != subject.id:
            self.add_error('topic', 'The selected topic must belong to the selected subject.')
        return cleaned_data


class TopicContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ('subject', 'title', 'content')
        widgets = {'content': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Describe the topic and why it should be added.'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.contribution_type = Contribution.TOPIC
        self.fields['subject'].required = True


class PaperContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ('subject', 'title', 'year', 'paper_file', 'content')
        widgets = {'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Optional note for the admin reviewer.'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.contribution_type = Contribution.PAPER
        self.fields['subject'].required = True
        self.fields['paper_file'].required = True


class ContributionReviewForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = ('admin_feedback',)


class TopicAwareMixin:
    @staticmethod
    def limit_topics(form):
        form.fields['topic'].queryset = Topic.objects.select_related('subject').all()
        form.fields['subject'].queryset = Subject.objects.all()
        return form
