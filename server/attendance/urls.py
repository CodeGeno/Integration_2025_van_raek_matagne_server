from django.urls import path
from .views import AttendanceCreation, AttendanceValidation

urlpatterns = [
    path('create/', AttendanceCreation, name='attendance-creation'),
    path('validate/', AttendanceValidation, name='attendance-validation'),
]
