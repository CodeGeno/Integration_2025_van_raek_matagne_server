from django.urls import path
from .views import StudentCreationEndpoint, EmployeeCreationEndpoint,Login  # Importez votre vue

urlpatterns = [
    path('create-student/', StudentCreationEndpoint.as_view(), name='create-student'),
    path('create-employee/', EmployeeCreationEndpoint.as_view(), name='create-employee'),
    path('login/', Login.as_view(), name='login'),
]
