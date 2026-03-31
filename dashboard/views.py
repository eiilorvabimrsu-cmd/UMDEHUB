from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count
from django.views.generic import TemplateView

from notes.models import Subject, Topic
from papers.models import PastPaper
from quizzes.models import Result


class HomeView(TemplateView):
    template_name = 'dashboard/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subject_count'] = Subject.objects.count()
        context['topic_count'] = Topic.objects.count()
        context['paper_count'] = PastPaper.objects.count()
        context['quiz_count'] = Result.objects.count()
        context['featured_subjects'] = Subject.objects.all()[:4]
        context['recent_papers'] = PastPaper.objects.select_related('subject')[:4]
        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        results = self.request.user.results.select_related('topic', 'subject')
        total_quizzes = results.count()
        average_score = results.aggregate(avg=Avg('percentage'))['avg'] or 0
        weak_topics = (
            results.exclude(topic__isnull=True)
            .values('topic__title', 'topic__subject__name')
            .annotate(avg_score=Avg('percentage'), attempts=Count('id'))
            .order_by('avg_score')[:5]
        )
        recent_activity = results[:5]
        leaderboard = (
            Result.objects.values('user__username')
            .annotate(avg_score=Avg('percentage'), attempts=Count('id'))
            .order_by('-avg_score', '-attempts')[:5]
        )
        context.update(
            {
                'total_quizzes': total_quizzes,
                'average_score': round(average_score, 1),
                'weak_topics': weak_topics,
                'recent_activity': recent_activity,
                'leaderboard': leaderboard,
            }
        )
        return context
