from django.urls import path
from .views import AttendanceUpsert, AttendanceValidation, StudentAcademicUeDropout, AttendanceListByLessonId

urlpatterns = [
    path('upsert/', AttendanceUpsert, name='attendance-upsert'),
    path('validate/', AttendanceValidation, name='attendance-validation'),
    path('dropout/<int:academicUeId>/<int:studentId>/', StudentAcademicUeDropout, name='student-academic-ue-dropout'),
    path('details/<int:lessonId>/', AttendanceListByLessonId, name='attendance-list'),
]
