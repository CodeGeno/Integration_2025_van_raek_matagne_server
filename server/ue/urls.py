from django.urls import path
from .views import UECreation, GetAllUEs, UpdateUEAndPrerequisites, DeleteUE, GetUEById

urlpatterns = [
    path('list/', GetAllUEs, name='get_all_ues'),
    path('create/', UECreation, name='create_ue'),
    path('update/<int:ue_id>/', UpdateUEAndPrerequisites, name='update_ue'),
    path('delete/<int:ue_id>/', DeleteUE, name='delete_ue'),  # Nouvelle URL pour désactiver l'UE
    path('<int:ue_id>/', GetUEById, name='get_ue_by_id'),
]