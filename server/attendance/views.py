from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Attendance
from .serializers import AttendanceSerializer
from security.decorators import checkRoleToken
from security.models import AccountRoleEnum
from api.models import ApiResponseClass
from django.db import transaction
# Create your views here.

@api_view(['POST'])
def AttendanceCreation(request):
    @checkRoleToken([AccountRoleEnum.PROFESSOR,AccountRoleEnum.ADMINISTRATOR])
    def wrapper(request):
        # Vérifier si les données envoyées sont une liste
        if isinstance(request.data, list):
            # Utiliser une transaction pour garantir l'atomicité
            with transaction.atomic():
                # Valider d'abord toutes les données avant de sauvegarder
                serializers = []
                all_valid = True
                validation_errors = []
                
                for index, attendance_data in enumerate(request.data):
                    serializer = AttendanceSerializer(data=attendance_data)
                    if serializer.is_valid():
                        serializers.append(serializer)
                    else:
                        all_valid = False
                        validation_errors.append({
                            "index": index,
                            "errors": serializer.errors
                        })
                
                # Si toutes les données sont valides, sauvegarder
                if all_valid:
                    created_attendances = [serializer.save() for serializer in serializers]
                    response_data = [AttendanceSerializer(attendance).data for attendance in created_attendances]
                    return ApiResponseClass.created("Toutes les présences ont été créées avec succès", response_data)
                else:
                    # Si une seule entrée est invalide, annuler la transaction et retourner les erreurs
                    transaction.set_rollback(True)
                    return ApiResponseClass.error({
                        "message": "La création des présences a échoué. Aucune présence n'a été créée.",
                        "errors": validation_errors
                    })
        else:
            # Traiter une seule présence si les données ne sont pas une liste
            serializer = AttendanceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ApiResponseClass.created("Présence créée avec succès", serializer.data)
            return ApiResponseClass.error(serializer.errors)
    return wrapper(request)
    
@api_view(['POST']) 
def AttendanceValidation(request):
    @checkRoleToken([AccountRoleEnum.ADMINISTRATOR])
    def wrapper(request):
        if request.method == 'POST':
            # Vérifier si les données envoyées sont une liste
            if isinstance(request.data, list):
                # Utiliser une transaction pour garantir l'atomicité
                with transaction.atomic():
                    # Valider d'abord toutes les données avant de sauvegarder
                    serializers = []
                    all_valid = True
                    validation_errors = []
                    
                    for index, attendance_data in enumerate(request.data):
                        serializer = AttendanceSerializer(data=attendance_data)
                        if serializer.is_valid():
                            serializers.append(serializer)
                        else:
                            all_valid = False
                            validation_errors.append({
                                "index": index,
                                "errors": serializer.errors
                            })
                    
                    # Si toutes les données sont valides, sauvegarder
                    if all_valid:
                        validated_attendances = [serializer.save() for serializer in serializers]
                        response_data = [AttendanceSerializer(attendance).data for attendance in validated_attendances]
                        return ApiResponseClass.created("Toutes les présences ont été validées avec succès", response_data)
                    else:
                        # Si une seule entrée est invalide, annuler la transaction et retourner les erreurs
                        transaction.set_rollback(True)
                        return ApiResponseClass.error({
                            "success": False,
                            "message": "La validation des présences a échoué. Aucune présence n'a été validée.",
                            "errors": validation_errors
                        }, status=status.HTTP_400_BAD_REQUEST)  
            else:
                # Traiter une seule présence si les données ne sont pas une liste
                serializer = AttendanceSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return ApiResponseClass.created("Présence validée avec succès", serializer.data)
                return ApiResponseClass.error(serializer.errors)
    return wrapper(request)