from django import forms
from django.forms import inlineformset_factory

from .models import CaseMedia, CaseStudy


class CaseStudyForm(forms.ModelForm):
    class Meta:
        model = CaseStudy
        fields = [
            'title',
            'patient_age',
            'patient_gender',
            'chief_complaint',
            'diagnosis',
            'treatment_plan',
            'management_steps',
            'discussion',
            'is_anonymized',
        ]
        widgets = {
            'chief_complaint': forms.Textarea(attrs={'rows': 4}),
            'diagnosis': forms.Textarea(attrs={'rows': 4}),
            'treatment_plan': forms.Textarea(attrs={'rows': 4}),
            'management_steps': forms.Textarea(attrs={'rows': 5}),
            'discussion': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_is_anonymized(self):
        value = self.cleaned_data['is_anonymized']
        if not value:
            raise forms.ValidationError('You must confirm that the case is fully anonymized before submission.')
        return value


CaseMediaFormSet = inlineformset_factory(
    CaseStudy,
    CaseMedia,
    fields=('file', 'media_type'),
    extra=1,
    can_delete=True,
)
