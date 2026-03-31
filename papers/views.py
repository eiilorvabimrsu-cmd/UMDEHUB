from django.db.models import Q
from django.shortcuts import render

from notes.models import Subject

from .models import PastPaper


def paper_list(request):
    subject_id = request.GET.get('subject')
    year = request.GET.get('year')
    query = request.GET.get('q', '').strip()

    papers = PastPaper.objects.select_related('subject').all()
    if subject_id:
        papers = papers.filter(subject_id=subject_id)
    if year:
        papers = papers.filter(year=year)
    if query:
        papers = papers.filter(Q(title__icontains=query) | Q(subject__name__icontains=query))

    years = PastPaper.objects.values_list('year', flat=True).distinct().order_by('-year')
    return render(
        request,
        'papers/paper_list.html',
        {
            'papers': papers,
            'subjects': Subject.objects.all(),
            'years': years,
            'selected_subject': subject_id,
            'selected_year': year,
            'query': query,
        },
    )
