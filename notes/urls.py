from django.urls import path

from .views import subject_list, subject_topics, topic_notes

app_name = 'notes'

urlpatterns = [
    path('subjects/', subject_list, name='subject_list'),
    path('subjects/<int:pk>/topics/', subject_topics, name='subject_topics'),
    path('topics/<int:pk>/notes/', topic_notes, name='topic_notes'),
]
