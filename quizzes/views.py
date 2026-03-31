import random
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from notes.models import Subject, Topic

from .models import AnswerRecord, Choice, Question, Result

QUIZ_MIN_QUESTIONS = 5
QUIZ_MAX_QUESTIONS = 10
MOCK_QUESTION_COUNT = 20
MOCK_DURATION_SECONDS = 30 * 60


def _block_practitioners(user):
    return hasattr(user, 'profile') and user.profile.is_practitioner and not user.is_staff


def _pick_questions(queryset, count):
    questions = list(
        queryset.prefetch_related(
            Prefetch('choices', queryset=Choice.objects.order_by('?'))
        )
    )
    random.shuffle(questions)
    return questions[: min(count, len(questions))]


def _questions_from_post(request):
    question_ids = request.POST.getlist('question_ids')
    if not question_ids:
        return []
    questions = list(
        Question.objects.filter(id__in=question_ids)
        .select_related('subject', 'topic')
        .prefetch_related(Prefetch('choices', queryset=Choice.objects.order_by('id')))
    )
    order_map = {str(question_id): index for index, question_id in enumerate(question_ids)}
    questions.sort(key=lambda question: order_map.get(str(question.id), 0))
    return questions


def _build_review_payload(questions, selected_map):
    review_items = []
    for question in questions:
        selected_choice = None
        selected_choice_id = selected_map.get(str(question.id))
        if selected_choice_id:
            selected_choice = next(
                (choice for choice in question.choices.all() if str(choice.id) == str(selected_choice_id)),
                None,
            )
        correct_choice = next((choice for choice in question.choices.all() if choice.is_correct), None)
        review_items.append(
            {
                'question': question,
                'selected_choice': selected_choice,
                'correct_choice': correct_choice,
                'is_correct': bool(selected_choice and selected_choice.is_correct),
            }
        )
    return review_items


def _save_result(user, questions, review_items, quiz_type, topic=None, duration_seconds=0):
    subject = topic.subject if topic else None
    total_questions = len(questions)
    score = sum(1 for item in review_items if item['is_correct'])
    percentage = (score / total_questions * 100) if total_questions else 0
    result = Result.objects.create(
        user=user,
        topic=topic,
        subject=subject,
        quiz_type=quiz_type,
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        duration_seconds=duration_seconds,
    )
    AnswerRecord.objects.bulk_create(
        [
            AnswerRecord(
                result=result,
                question=item['question'],
                selected_choice=item['selected_choice'],
                is_correct=item['is_correct'],
            )
            for item in review_items
        ]
    )
    return result


@login_required
def topic_quiz(request, topic_id):
    if _block_practitioners(request.user):
        return HttpResponseForbidden('Practitioners can access notes, past papers, and case studies only.')
    topic = get_object_or_404(Topic.objects.select_related('subject'), pk=topic_id)
    questions = _pick_questions(topic.questions.all(), QUIZ_MAX_QUESTIONS)
    if len(questions) < QUIZ_MIN_QUESTIONS:
        messages.warning(request, 'This topic needs at least 5 questions before a quiz can run.')
        return redirect('notes:topic_notes', pk=topic.pk)

    if request.method == 'POST':
        questions = _questions_from_post(request)
        selected_map = {key.split('_')[1]: value for key, value in request.POST.items() if key.startswith('question_')}
        review_items = _build_review_payload(questions, selected_map)
        result = _save_result(request.user, questions, review_items, Result.TOPIC, topic=topic)
        return render(
            request,
            'quizzes/quiz_result.html',
            {'quiz_title': f'{topic.title} Quiz', 'result': result, 'review_items': review_items},
        )

    return render(
        request,
        'quizzes/quiz_take.html',
        {
            'quiz_title': f'{topic.title} Quiz',
            'quiz_description': f'Focused practice for {topic.subject.name}.',
            'questions': questions,
            'show_timer': False,
        },
    )


@login_required
def random_quiz(request):
    if _block_practitioners(request.user):
        return HttpResponseForbidden('Practitioners can access notes, past papers, and case studies only.')
    subject_id = request.GET.get('subject')
    question_pool = Question.objects.select_related('subject', 'topic').all()
    selected_subject = None
    if subject_id:
        selected_subject = get_object_or_404(Subject, pk=subject_id)
        question_pool = question_pool.filter(subject=selected_subject)

    questions = _pick_questions(question_pool, QUIZ_MAX_QUESTIONS)
    if len(questions) < QUIZ_MIN_QUESTIONS:
        messages.warning(request, 'There are not enough questions available for a random quiz yet.')
        return redirect('notes:subject_list')

    if request.method == 'POST':
        questions = _questions_from_post(request)
        selected_map = {key.split('_')[1]: value for key, value in request.POST.items() if key.startswith('question_')}
        review_items = _build_review_payload(questions, selected_map)
        result = _save_result(request.user, questions, review_items, Result.RANDOM)
        return render(
            request,
            'quizzes/quiz_result.html',
            {'quiz_title': 'Random Quiz', 'result': result, 'review_items': review_items},
        )

    return render(
        request,
        'quizzes/quiz_take.html',
        {
            'quiz_title': 'Random Mixed Quiz',
            'quiz_description': 'A shuffled set of questions across your available dental content.',
            'questions': questions,
            'show_timer': False,
            'subjects': Subject.objects.all(),
            'selected_subject': selected_subject,
        },
    )


@login_required
def mock_exam(request):
    if _block_practitioners(request.user):
        return HttpResponseForbidden('Practitioners can access notes, past papers, and case studies only.')
    questions = _pick_questions(Question.objects.select_related('subject', 'topic').all(), MOCK_QUESTION_COUNT)
    if len(questions) < QUIZ_MIN_QUESTIONS:
        messages.warning(request, 'Add more questions before running the mock exam.')
        return redirect('dashboard:overview')

    if request.method == 'POST':
        questions = _questions_from_post(request)
        selected_map = {key.split('_')[1]: value for key, value in request.POST.items() if key.startswith('question_')}
        started_at_raw = request.POST.get('started_at')
        duration_seconds = 0
        if started_at_raw:
            started_at = datetime.fromisoformat(started_at_raw)
            if timezone.is_naive(started_at):
                started_at = timezone.make_aware(started_at, timezone.get_current_timezone())
            duration_seconds = int((timezone.now() - started_at).total_seconds())
        duration_seconds = min(max(duration_seconds, 0), MOCK_DURATION_SECONDS)

        review_items = _build_review_payload(questions, selected_map)
        result = _save_result(request.user, questions, review_items, Result.MOCK, duration_seconds=duration_seconds)
        return render(
            request,
            'quizzes/quiz_result.html',
            {'quiz_title': 'Mock Exam', 'result': result, 'review_items': review_items},
        )

    return render(
        request,
        'quizzes/quiz_take.html',
        {
            'quiz_title': '30-Minute Mock Exam',
            'quiz_description': 'Simulate exam pressure with a timed mixed-subject assessment.',
            'questions': questions,
            'show_timer': True,
            'duration_seconds': MOCK_DURATION_SECONDS,
            'started_at': timezone.now().isoformat(),
        },
    )


@login_required
def result_history(request):
    if _block_practitioners(request.user):
        return HttpResponseForbidden('Practitioners can access notes, past papers, and case studies only.')
    results = request.user.results.select_related('subject', 'topic')
    return render(request, 'quizzes/result_history.html', {'results': results})
