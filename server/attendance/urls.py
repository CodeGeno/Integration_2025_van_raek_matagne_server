from django.urls import path
from .views import AttendanceUpsertView, AttendanceValidationView, StudentAcademicUeDropoutView, AttendanceListByLessonIdView

urlpatterns = [
    path('upsert/', AttendanceUpsertView.as_view(), name='attendance-upsert'),
    path('validate/', AttendanceValidationView.as_view(), name='attendance-validation'),
    path('dropout/<int:academicUeId>/<int:studentId>/', StudentAcademicUeDropoutView.as_view(), name='student-academic-ue-dropout'),
    path('details/<int:lessonId>/', AttendanceListByLessonIdView.as_view(), name='attendance-list'),
]
