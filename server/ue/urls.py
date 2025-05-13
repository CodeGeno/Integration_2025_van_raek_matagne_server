from django.urls import path
from .views import UECreationView, GetAllUEsView, UpdateUEAndPrerequisitesView, DeleteUEView, GetUEByIdView

urlpatterns = [
    path('list/', GetAllUEsView.as_view(), name='get_all_ues'),
    path('create/', UECreationView.as_view(), name='create_ue'),
    path('update/<int:ue_id>/', UpdateUEAndPrerequisitesView.as_view(), name='update_ue'),
    path('delete/<int:ue_id>/', DeleteUEView.as_view(), name='delete_ue'),
    path('<int:ue_id>/', GetUEByIdView.as_view(), name='get_ue_by_id'),
]