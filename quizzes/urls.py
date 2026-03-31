from django.urls import path

from .views import mock_exam, random_quiz, result_history, topic_quiz

app_name = 'quizzes'

urlpatterns = [
    path('quiz/<int:topic_id>/', topic_quiz, name='topic_quiz'),
    path('quiz/random/', random_quiz, name='random_quiz'),
    path('mock-exam/', mock_exam, name='mock_exam'),
    path('results/', result_history, name='result_history'),
]
