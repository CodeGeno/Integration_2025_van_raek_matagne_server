# server/ue_management/urls.py
from django.urls import path

from ue_management.views import (
    AcademicUEListView, AcademicUEDetailView,
    LessonListView, LessonDetailView,
    ResultListView, ResultDetailView, AcademicUEGetById,
    GenerateNextYearUEsView, SectionRegistration,
    RegisterStudentsToAcademicUE, GetStudentResults
)

urlpatterns = [
    path('academic-ues/', AcademicUEListView.as_view(), name='academic-ue-list'),
    path('academic-ues/<int:pk>/', AcademicUEDetailView.as_view(), name='academic-ue-detail'),
    path('lessons/', LessonListView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('results/', ResultListView.as_view(), name='result-list'),
    path('results/<int:pk>/', ResultDetailView.as_view(), name='result-detail'),
    path('results/<int:academic_ue>/<int:student>/', GetStudentResults, name='get-student-results'),
    path('generate-next-year/', GenerateNextYearUEsView.as_view(), name='generate-next-year'),
    path('academic-ues/<int:id>/', AcademicUEGetById, name='academic-ue-get-by-id'),
    path('academic-ues/<int:id>/register-section/', SectionRegistration, name='section-registration'),
    path('academic-ues/<int:id>/register-students/', RegisterStudentsToAcademicUE, name='register-students'),
    
]
