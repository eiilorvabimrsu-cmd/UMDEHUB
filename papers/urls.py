from django.urls import path

from .views import paper_list

app_name = 'papers'

urlpatterns = [
    path('', paper_list, name='paper_list'),
]
