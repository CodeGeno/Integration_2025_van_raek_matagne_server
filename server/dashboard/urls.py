from django.urls import path
from .views import StudentDashboardView, TeacherDashboardView

urlpatterns = [
    path('student/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('teacher/', TeacherDashboardView.as_view(), name='teacher-dashboard'),
] 