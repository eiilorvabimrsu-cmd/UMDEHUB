from django.urls import path

from .views import (
    contribute_note,
    contribute_paper,
    contribute_topic,
    contribute_video,
    contribution_home,
    import_list,
    import_questions,
    import_review,
)

app_name = 'contributions'

urlpatterns = [
    path('', contribution_home, name='home'),
    path('notes/', contribute_note, name='note'),
    path('videos/', contribute_video, name='video'),
    path('topics/', contribute_topic, name='topic'),
    path('papers/', contribute_paper, name='paper'),
    path('imports/', import_list, name='import_list'),
    path('imports/new/', import_questions, name='import_questions'),
    path('imports/<int:pk>/review/', import_review, name='import_review'),
]
