from django.urls import path
from .views import AttendanceCreation, AttendanceValidation, StudentAcademicUeDropout

urlpatterns = [
    path('create/', AttendanceCreation, name='attendance-creation'),
    path('validate/', AttendanceValidation, name='attendance-validation'),
    path('dropout/<int:academicUeId>/<int:studentId>/', StudentAcademicUeDropout, name='student-academic-ue-dropout'),
]
