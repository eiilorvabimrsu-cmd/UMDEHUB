from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, render

from contributions.models import StudyVideo

from .models import Note, Subject, Topic


def subject_list(request):
    query = request.GET.get('q', '').strip()
    subjects = Subject.objects.all()
    if query:
        subjects = subjects.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return render(request, 'notes/subject_list.html', {'subjects': subjects, 'query': query})


def subject_topics(request, pk):
    subject = get_object_or_404(
        Subject.objects.prefetch_related(
            Prefetch('topics', queryset=Topic.objects.order_by('title'))
        ),
        pk=pk,
    )
    return render(request, 'notes/topic_list.html', {'subject': subject})


def topic_notes(request, pk):
    topic = get_object_or_404(
        Topic.objects.select_related('subject').prefetch_related(
            Prefetch('notes', queryset=Note.objects.order_by('title'))
        ),
        pk=pk,
    )
    videos = StudyVideo.objects.filter(topic=topic).order_by('title')
    return render(request, 'notes/note_detail.html', {'topic': topic, 'videos': videos})
