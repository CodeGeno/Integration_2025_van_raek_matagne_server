from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UE
from .serializers import UESerializer
from api.models import ApiResponseClass

# Create your views here.

@api_view(['POST'])
def UECreation(request):
    try:
        serializer = UESerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ApiResponseClass.created("UE créée avec succès", serializer.data)
        return ApiResponseClass.error("Erreur lors de la création de l'UE", serializer.errors)
    except Exception as e:
        return ApiResponseClass.error(f"Une erreur inattendue s'est produite: {str(e)}")

@api_view(['GET'])
def GetAllUEs(request):
    try:
        ues = UE.objects.all()
        serializer = UESerializer(ues, many=True)
        return ApiResponseClass.success("Liste des UEs récupérée avec succès", serializer.data)
    except Exception as e:
        return ApiResponseClass.error(f"Une erreur s'est produite lors de la récupération des UEs: {str(e)}")


@api_view(['PATCH'])
def UpdateUE(request, ue_id):
    try:
        ue = get_object_or_404(UE, ueId=ue_id)
        serializer = UESerializer(ue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ApiResponseClass.success("UE mise à jour avec succès", serializer.data)
        return ApiResponseClass.error("Erreur lors de la mise à jour de l'UE", serializer.errors)
    except Exception as e:
        return ApiResponseClass.error(f"Une erreur s'est produite lors de la mise à jour de l'UE: {str(e)}")

@api_view(['PATCH'])
def UpdateUEPrerequisites(request, ue_id):
    # Mettre à jour l'UE avec les informations des UEs associées
    try:
        ue = get_object_or_404(UE, ueId=ue_id)
        
        # Vérifier si les prérequis sont fournis dans la requête
        if 'prerequisites' not in request.data:
            return ApiResponseClass.error("Les prérequis ne sont pas fournis dans la requête")
        
        # Récupérer les objets prérequis
        prerequisites_data = request.data.get('prerequisites', [])
        
        # Effacer les prérequis actuels
        ue.prerequisites.clear()
        
        # Traiter chaque prérequis
        for prereq_data in prerequisites_data:
            # Si l'objet contient juste un ID
            if isinstance(prereq_data, int):
                prereq_id = prereq_data
            # Si l'objet est un dictionnaire avec un ID
            elif isinstance(prereq_data, dict) and 'ueId' in prereq_data:
                prereq_id = prereq_data['ueId']
            else:
                continue  # Ignorer les entrées mal formatées
                
            try:
                prereq_ue = UE.objects.get(ueId=prereq_id)
                # Vérifier que l'UE ne se référence pas elle-même
                if prereq_ue.ueId != ue_id:
                    ue.prerequisites.add(prereq_ue)
            except UE.DoesNotExist:
                # Ignorer les IDs qui n'existent pas
                continue
                
        # Récupérer l'UE mise à jour avec ses prérequis
        updated_ue = UE.objects.get(ueId=ue_id)
        serializer = UESerializer(updated_ue)
        
        return ApiResponseClass.success("Prérequis de l'UE mis à jour avec succès", serializer.data)
    except Exception as e:
        return ApiResponseClass.error(f"Une erreur s'est produite lors de la mise à jour des prérequis: {str(e)}")
       