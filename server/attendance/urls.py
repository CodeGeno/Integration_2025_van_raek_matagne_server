from django.urls import path
from .views import AttendanceCreation, AttendanceValidation, StudentAcademicUeDropout, AttendanceListByLessonId

urlpatterns = [
    path('create/', AttendanceCreation, name='attendance-creation'),
    path('validate/', AttendanceValidation, name='attendance-validation'),
    path('dropout/<int:academicUeId>/<int:studentId>/', StudentAcademicUeDropout, name='student-academic-ue-dropout'),
    path('details/<int:lessonId>/', AttendanceListByLessonId, name='attendance-list'),
]
