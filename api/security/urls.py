from django.urls import path
from .views import AccountCreationEndpoint  # Importez votre vue

urlpatterns = [
    path('create-account/', AccountCreationEndpoint.as_view(), name='create-account'),  # Endpoint pour créer un compte
]
