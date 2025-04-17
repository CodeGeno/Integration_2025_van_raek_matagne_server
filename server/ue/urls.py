from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.UECreation, name='ue-creation'),
    path('list/', views.GetAllUEs, name='get-all-ues'),
    path('update/<int:ue_id>/', views.UpdateUE, name='update-ue'),
    path('update-prerequisites/<int:ue_id>/', views.UpdateUEPrerequisites, name='update-ue-prerequisites'),
]