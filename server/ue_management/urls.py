# server/ue_management/urls.py
from django.urls import path

from ue_management.views import (
    AcademicUEListView, AcademicUEDetailView,
    LessonListView, LessonDetailView,
    ResultListView, ResultDetailView, AcademicUEGetById,
    SectionRegistration,
    RegisterStudentsToAcademicUE, GetStudentResults,
    GetStudentAcademicUEs, GetEligibleStudentsForAcademicUE,
    StudentAcademicUeRegistration, GetStudentAcademicUEDetails
)

urlpatterns = [
    path('academic-ues/', AcademicUEListView.as_view(), name='academic-ue-list'),
    path('academic-ues/<int:pk>/', AcademicUEDetailView.as_view(), name='academic-ue-detail'),
    path('lessons/', LessonListView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('results/', ResultListView.as_view(), name='result-list'),
    path('results/<int:academic_ue>/<int:student>/', GetStudentResults.as_view(), name='get-student-results'),
    path('results/<int:pk>/', ResultDetailView.as_view(), name='result-detail'),
    path('academic-ues/<int:id>/', AcademicUEGetById.as_view(), name='academic-ue-get-by-id'),
    path('register-section/', SectionRegistration.as_view(), name='section-registration'),
    path('academic-ues/student/details/<int:student_id>/', GetStudentAcademicUEDetails.as_view(), name='get-student-academic-ue-details'),
    path('academic-ues/<int:id>/register-students/', RegisterStudentsToAcademicUE.as_view(), name='register-students'),
    path('academic-ues/<int:academicUeId>/students/<int:studentId>/register/', StudentAcademicUeRegistration.as_view(), name='student-academic-ue-register'),
    path('academic-ues/student/<int:student_id>/', GetStudentAcademicUEs.as_view(), name='get-student-academic-ues'),
    path('academic-ues/registration/students/<int:academicUeId>/', GetEligibleStudentsForAcademicUE.as_view(), name='get-eligible-students'),
]
