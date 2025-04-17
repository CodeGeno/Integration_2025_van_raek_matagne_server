# server/ue_management/urls.py
from django.urls import path
from .views import AcademicUEView, LessonView, ResultView

urlpatterns = [
    path('academic-ues/', AcademicUEView.as_view(), name='academic-ue-list'),
    path('academic-ues/<int:pk>/', AcademicUEView.as_view(), name='academic-ue-detail'),
    path('lessons/', LessonView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonView.as_view(), name='lesson-detail'),
    path('results/', ResultView.as_view(), name='result-list'),
    path('results/<int:pk>/', ResultView.as_view(), name='result-detail'),
]