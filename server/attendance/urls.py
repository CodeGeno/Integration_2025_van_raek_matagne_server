from django.urls import path
from .views import (
    AttendanceUpsertView,
    AttendanceValidationView,
    StudentAcademicUeDropoutView,
    AttendanceListByLessonIdView,
    AttendanceSummaryView,
)

urlpatterns = [
    path('upsert/', AttendanceUpsertView.as_view(), name='attendance-upsert'),
    path('validate/', AttendanceValidationView.as_view(), name='attendance-validate'),
    path('dropout/<int:academicUeId>/<int:studentId>/', StudentAcademicUeDropoutView.as_view(), name='student-academic-ue-dropout'),
    path('details/<int:lessonId>/', AttendanceListByLessonIdView.as_view(), name='attendance-list'),
    path('summary/<int:academic_ue_id>/', AttendanceSummaryView.as_view(), name='attendance-summary'),
]
