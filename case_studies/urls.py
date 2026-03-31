from django.urls import path

from .views import (
    case_create,
    case_delete,
    case_detail,
    case_edit,
    case_list,
    practitioner_dashboard,
)

app_name = 'case_studies'

urlpatterns = [
    path('cases/', case_list, name='case_list'),
    path('cases/<int:pk>/', case_detail, name='case_detail'),
    path('practitioner/cases/', practitioner_dashboard, name='practitioner_dashboard'),
    path('practitioner/cases/new/', case_create, name='case_create'),
    path('practitioner/cases/<int:pk>/edit/', case_edit, name='case_edit'),
    path('practitioner/cases/<int:pk>/delete/', case_delete, name='case_delete'),
]
