from django.urls import path
from .views import SectionCreation, GetAllSections

urlpatterns = [
    path('section/create/', SectionCreation, name='section-creation'),
    path('/', GetAllSections, name='get-all-sections'),
]
