from django.urls import path
from .views import SectionCreationView, GetAllSectionsView, DeleteSectionView, UpdateSectionView, GetSectionByIdView

urlpatterns = [
    path('create/', SectionCreationView.as_view(), name='section-creation'),
    path('list/', GetAllSectionsView.as_view(), name='get-all-sections'),
    path('delete/<int:section_id>/', DeleteSectionView.as_view(), name='delete-section'),
    path('update/<int:section_id>/', UpdateSectionView.as_view(), name='update-section'),
    path('<int:section_id>/', GetSectionByIdView.as_view(), name='get-section-by-id'),
]
