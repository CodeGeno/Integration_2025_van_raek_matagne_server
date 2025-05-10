# server/ue_management/urls.py
from django.urls import path

from ue_management.views import (
    AcademicUEListView, AcademicUEDetailView,
    LessonListView, LessonDetailView,
    ResultListView, ResultDetailView, AcademicUEGetById,
    GenerateNextYearUEsView, SectionRegistration, StudentStatusGetByAcademicUeId,
    StudentAcademicUeRegistration
)

urlpatterns = [
    path('academic-ues/', AcademicUEListView.as_view(), name='ue-management_academic-ues_list'),
    path('academic-ues/<int:pk>/', AcademicUEDetailView.as_view(), name='ue-management_academic-ues_read'),
    path('academic-ues/generate-next-year/', GenerateNextYearUEsView.as_view(), name='ue-management_generate-next-year'),
    path('lessons/', LessonListView.as_view(), name='ue-management_lessons_list'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='ue-management_lessons_read'),
    path('results/', ResultListView.as_view(), name='ue-management_results_list'),
    path('results/<int:pk>/', ResultDetailView.as_view(), name='ue-management_results_read'),
    path('academic-ues/register/<int:id>/', AcademicUEGetById, name='ue-management_academic-ues_create'),
    path('section/register/', SectionRegistration, name='ue-management_section_create'),
    path('academic-ues/registration/students/<int:academicUeId>/', StudentStatusGetByAcademicUeId, name='ue-management_students-status_get'),
    path('academic-ues/<int:academicUeId>/students/<int:studentId>/register/', StudentAcademicUeRegistration, name='ue-management_student-register'),
]
