# server/ue_management/urls.py
from django.urls import path

from ue_management.views import (
    AcademicUEListView, AcademicUEDetailView,
    LessonListView, LessonDetailView,
    ResultListView, ResultDetailView,
    AcademicUEGetById
)

urlpatterns = [
    path('academic-ues/', AcademicUEListView.as_view(), name='ue-management_academic-ues_list'),
    path('academic-ues/<int:pk>/', AcademicUEDetailView.as_view(), name='ue-management_academic-ues_read'),
    path('lessons/', LessonListView.as_view(), name='ue-management_lessons_list'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='ue-management_lessons_read'),
    path('results/', ResultListView.as_view(), name='ue-management_results_list'),
    path('results/<int:pk>/', ResultDetailView.as_view(), name='ue-management_results_read'),
    path('academic-ues/register/<int:id>/', AcademicUEGetById, name='ue-management_academic-ues_create'),
   
]