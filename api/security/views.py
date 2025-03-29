# api/security/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .decorators import jwt_required
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

   
class AccountCreationEndpoint(APIView):
    def post(self, request, *args, **kwargs):
        request_data = request.data
        print(request_data)
        # Logique pour créer un compte
        return Response({"message": "Compte créé avec succès"}, status=status.HTTP_201_CREATED)
        

