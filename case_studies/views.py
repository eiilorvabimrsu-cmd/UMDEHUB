from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CaseMediaFormSet, CaseStudyForm
from .models import CaseStudy


def _is_practitioner(user):
    return (
        user.is_authenticated
        and hasattr(user, 'profile')
        and user.profile.is_practitioner
        and user.profile.practitioner_approved
    )


def _is_student(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_student


@login_required
def case_list(request):
    if request.user.is_staff:
        cases = CaseStudy.objects.select_related('practitioner').all()
    else:
        cases = CaseStudy.objects.select_related('practitioner').filter(status=CaseStudy.APPROVED)
    return render(request, 'case_studies/case_list.html', {'cases': cases})


@login_required
def case_detail(request, pk):
    case = get_object_or_404(CaseStudy.objects.select_related('practitioner'), pk=pk)
    if not request.user.is_staff and case.status != CaseStudy.APPROVED:
        if not _is_practitioner(request.user) or case.practitioner_id != request.user.id:
            return HttpResponseForbidden('You cannot view this case study.')
    return render(request, 'case_studies/case_detail.html', {'case': case})


@login_required
def practitioner_dashboard(request):
    if not _is_practitioner(request.user):
        return HttpResponseForbidden('Practitioner approval is required to access this page.')
    cases = request.user.case_studies.all()
    return render(request, 'case_studies/practitioner_dashboard.html', {'cases': cases})


@login_required
def case_create(request):
    if not _is_practitioner(request.user):
        return HttpResponseForbidden('Practitioner approval is required to upload case studies.')

    if request.method == 'POST':
        form = CaseStudyForm(request.POST)
        formset = CaseMediaFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            case = form.save(commit=False)
            case.practitioner = request.user
            case.status = CaseStudy.PENDING
            case.save()
            formset.instance = case
            formset.save()
            messages.success(request, 'Case study submitted for admin review.')
            return redirect('case_studies:practitioner_dashboard')
    else:
        form = CaseStudyForm()
        formset = CaseMediaFormSet()

    return render(
        request,
        'case_studies/case_form.html',
        {'form': form, 'formset': formset, 'page_title': 'Upload New Case Study'},
    )


@login_required
def case_edit(request, pk):
    if not _is_practitioner(request.user):
        return HttpResponseForbidden('Practitioner approval is required to edit case studies.')

    case = get_object_or_404(CaseStudy, pk=pk, practitioner=request.user)
    if request.method == 'POST':
        form = CaseStudyForm(request.POST, instance=case)
        formset = CaseMediaFormSet(request.POST, request.FILES, instance=case)
        if form.is_valid() and formset.is_valid():
            edited_case = form.save(commit=False)
            edited_case.status = CaseStudy.PENDING
            edited_case.save()
            formset.save()
            messages.success(request, 'Case study updated and sent back for admin review.')
            return redirect('case_studies:practitioner_dashboard')
    else:
        form = CaseStudyForm(instance=case)
        formset = CaseMediaFormSet(instance=case)

    return render(
        request,
        'case_studies/case_form.html',
        {'form': form, 'formset': formset, 'page_title': 'Edit Case Study', 'case': case},
    )


@login_required
def case_delete(request, pk):
    if not _is_practitioner(request.user):
        return HttpResponseForbidden('Practitioner approval is required to delete case studies.')

    case = get_object_or_404(CaseStudy, pk=pk, practitioner=request.user)
    if request.method == 'POST':
        case.delete()
        messages.success(request, 'Case study deleted.')
        return redirect('case_studies:practitioner_dashboard')
    return render(request, 'case_studies/case_delete.html', {'case': case})
