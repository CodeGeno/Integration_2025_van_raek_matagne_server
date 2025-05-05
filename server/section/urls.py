from django.urls import path
from .views import SectionCreation, GetAllSections, DeleteSection, UpdateSection, GetSectionById

urlpatterns = [
    path('create/', SectionCreation, name='section-creation'),
    path('list/', GetAllSections, name='get-all-sections'),
    path('delete/<int:section_id>/', DeleteSection, name='delete-section'),
    path('update/<int:section_id>/', UpdateSection, name='update-section'),
    path('<int:section_id>/', GetSectionById, name='get-section-by-id'),
]
