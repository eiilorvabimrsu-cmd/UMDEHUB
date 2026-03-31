from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from quizzes.models import Choice, Question

from .forms import (
    NoteContributionForm,
    PaperContributionForm,
    QuestionImportForm,
    TopicContributionForm,
    VideoContributionForm,
)
from .models import Contribution, ImportedChoice, ImportedQuestion, QuestionImportBatch
from .utils import extract_text_from_docx, extract_text_from_pdf, parse_questions_from_text


def staff_required(view_func):
    return user_passes_test(lambda user: user.is_staff)(view_func)


def _process_import_batch(batch):
    extension = batch.source_file.name.rsplit('.', 1)[-1].lower()
    batch.source_type = extension
    file_path = batch.source_file.path

    if extension == 'docx':
        extracted_text, scanned_detected, parser_notes = extract_text_from_docx(file_path)
    else:
        extracted_text, scanned_detected, parser_notes = extract_text_from_pdf(file_path)

    batch.extracted_text = extracted_text
    batch.scanned_detected = scanned_detected
    batch.parser_notes = parser_notes
    batch.status = QuestionImportBatch.SCANNED_ONLY if scanned_detected else QuestionImportBatch.READY
    batch.save(update_fields=['source_type', 'extracted_text', 'scanned_detected', 'parser_notes', 'status'])

    batch.questions.all().delete()
    if scanned_detected:
        return 0

    parsed_questions = parse_questions_from_text(extracted_text)
    for item in parsed_questions:
        imported_question = ImportedQuestion.objects.create(
            batch=batch,
            order=item['order'],
            text=item['text'],
            detected_answer_label=item.get('detected_answer_label', ''),
        )
        for choice in item['choices']:
            ImportedChoice.objects.create(
                question=imported_question,
                label=choice['label'],
                text=choice['text'],
                is_selected_correct=choice['label'] == item.get('detected_answer_label', ''),
            )
    return len(parsed_questions)


@login_required
def contribution_home(request):
    submissions = request.user.contributions.select_related('subject', 'topic')[:8]
    return render(request, 'contributions/home.html', {'submissions': submissions})


def _save_contribution(request, form_class, contribution_type, template_name, success_message):
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.user = request.user
            contribution.contribution_type = contribution_type
            contribution.save()
            messages.success(request, success_message)
            return redirect('contributions:home')
    else:
        form = form_class()
    return render(request, template_name, {'form': form})


@login_required
def contribute_note(request):
    return _save_contribution(
        request,
        NoteContributionForm,
        Contribution.NOTE,
        'contributions/form.html',
        'Your note submission has been sent for admin review.',
    )


@login_required
def contribute_video(request):
    return _save_contribution(
        request,
        VideoContributionForm,
        Contribution.VIDEO,
        'contributions/form.html',
        'Your study video suggestion has been sent for admin review.',
    )


@login_required
def contribute_topic(request):
    return _save_contribution(
        request,
        TopicContributionForm,
        Contribution.TOPIC,
        'contributions/form.html',
        'Your topic suggestion has been sent for admin review.',
    )


@login_required
def contribute_paper(request):
    return _save_contribution(
        request,
        PaperContributionForm,
        Contribution.PAPER,
        'contributions/form.html',
        'Your past paper submission has been sent for admin review.',
    )


@staff_required
def import_questions(request):
    if request.method == 'POST':
        form = QuestionImportForm(request.POST, request.FILES)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.uploaded_by = request.user
            batch.save()
            parsed_count = _process_import_batch(batch)

            if batch.scanned_detected:
                messages.warning(
                    request,
                    'This PDF appears to be scanned. Please upload it to Past Papers only, not question import.',
                )
                return redirect('contributions:import_list')

            if parsed_count == 0:
                messages.warning(request, 'No structured questions were detected. Please review the document format.')
                return redirect('contributions:import_list')

            messages.success(request, f'{parsed_count} questions were imported. Please review and set correct answers.')
            return redirect('contributions:import_review', pk=batch.pk)
    else:
        form = QuestionImportForm()

    return render(request, 'contributions/import_form.html', {'form': form})


@staff_required
def import_list(request):
    batches = QuestionImportBatch.objects.select_related('subject', 'topic', 'uploaded_by')
    return render(request, 'contributions/import_list.html', {'batches': batches})


@staff_required
def import_review(request, pk):
    batch = get_object_or_404(
        QuestionImportBatch.objects.select_related('subject', 'topic').prefetch_related('questions__choices'),
        pk=pk,
    )
    questions = batch.questions.all()

    if request.method == 'POST':
        if batch.status == QuestionImportBatch.PUBLISHED:
            messages.info(request, 'This import batch has already been published.')
            return redirect('contributions:import_list')

        missing_answers = []
        for imported_question in questions:
            selected_choice_id = request.POST.get(f'correct_{imported_question.id}')
            explanation = request.POST.get(f'explanation_{imported_question.id}', '').strip()
            if not selected_choice_id:
                missing_answers.append(imported_question.order)
                continue

            imported_question.explanation = explanation
            imported_question.save(update_fields=['explanation'])
            imported_question.choices.update(is_selected_correct=False)
            imported_question.choices.filter(pk=selected_choice_id).update(is_selected_correct=True)

        if missing_answers:
            messages.error(request, f'Please choose a correct answer for questions: {", ".join(map(str, missing_answers))}.')
            return redirect('contributions:import_review', pk=batch.pk)

        if 'publish' in request.POST:
            for imported_question in questions:
                question = Question.objects.create(
                    text=imported_question.text,
                    subject=batch.subject,
                    topic=batch.topic,
                    difficulty=Question.BEGINNER,
                    explanation=imported_question.explanation,
                )
                fresh_choices = ImportedChoice.objects.filter(question=imported_question).order_by('label')
                Choice.objects.bulk_create(
                    [
                        Choice(
                            question=question,
                            text=choice.text,
                            is_correct=choice.is_selected_correct,
                        )
                        for choice in fresh_choices
                    ]
                )
            batch.status = QuestionImportBatch.PUBLISHED
            batch.published_at = timezone.now()
            batch.save(update_fields=['status', 'published_at'])
            messages.success(request, 'Questions published successfully and are now available for quizzes.')
            return redirect('contributions:import_list')

        messages.success(request, 'Correct answers saved for this import batch.')
        return redirect('contributions:import_review', pk=batch.pk)

    return render(request, 'contributions/import_review.html', {'batch': batch, 'questions': questions})
