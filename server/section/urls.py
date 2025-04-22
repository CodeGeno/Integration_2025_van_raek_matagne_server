from django.urls import path
from .views import SectionCreation, GetAllSections, DeleteSection

urlpatterns = [
    path('create/', SectionCreation, name='section-creation'),
    path('list/', GetAllSections, name='get-all-sections'),
    path('delete/<int:section_id>/', DeleteSection, name='delete-section'),
]
