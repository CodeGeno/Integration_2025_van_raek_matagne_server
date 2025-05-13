from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UE
from .serializers import UESerializer
from api.models import ApiResponseClass
from django.db.utils import IntegrityError

# Create your views here.
@api_view(['GET'])
def GetAllUEs(request):
    try:
        ues = UE.objects.all()
        serializer = UESerializer(ues, many=True)
        return ApiResponseClass.success("Liste des UEs récupérée avec succès", serializer.data)
    except Exception as e:
        return ApiResponseClass.error(f"Une erreur s'est produite lors de la récupération des UEs: {str(e)}")
    
@api_view(['GET'])
def GetUEById(request, ue_id):
    try:
        ue = get_object_or_404(UE, id=ue_id)
        serializer = UESerializer(ue)
        return ApiResponseClass.success("UE récupérée avec succès", serializer.data)
    except Exception as e:
        return ApiResponseClass.error(f"Une erreur s'est produite lors de la récupération de l'UE: {str(e)}")
       
@api_view(['POST'])
def UECreation(request):
    try:
        # Extraire les prérequis de la requête
        prerequisites_data = request.data.pop('prerequisites', [])
        
        # Créer l'UE sans les prérequis d'abord
        serializer = UESerializer(data=request.data)
        if serializer.is_valid():
            ue = serializer.save()
            
            # Ajouter les prérequis
            if prerequisites_data:
                for prereq_id in prerequisites_data:
                    try:
                        prereq_ue = UE.objects.get(id=prereq_id)
                        # Vérifier que le cycle du prérequis est inférieur ou égal à celui de l'UE
                        if prereq_ue.cycle <= ue.cycle:
                            ue.prerequisites.add(prereq_ue)
                        else:
                            return ApiResponseClass.error(f"Le prérequis {prereq_ue.name} est d'un cycle supérieur à l'UE.")
                    except UE.DoesNotExist:
                        return ApiResponseClass.error(f"Le prérequis {prereq_id} n'existe pas.")
            
            # Récupérer l'UE avec ses prérequis pour la réponse
            updated_ue = UE.objects.get(id=ue.id)
            response_serializer = UESerializer(updated_ue)
            return ApiResponseClass.created("UE créée avec succès", response_serializer.data)
        
        # Traitement détaillé des erreurs de sérialisation
        error_details = []
        for field, errors in serializer.errors.items():
            if isinstance(errors, list):
                for error in errors:
                    error_details.append(f"{field}: {error}")
            else:
                error_details.append(f"{field}: {errors}")
        
        error_message = "Erreurs de validation :\n" + "\n".join(error_details)
        return ApiResponseClass.error(error_message, status_code=status.HTTP_400_BAD_REQUEST)
    except ValueError as e:
        return ApiResponseClass.error(f"Erreur de valeur: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)
    except TypeError as e:
        return ApiResponseClass.error(f"Erreur de type: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)
    except IntegrityError as e:
        return ApiResponseClass.error("Cette UE existe déjà dans la base de données", status_code=status.HTTP_409_CONFLICT)
    except PermissionError:
        return ApiResponseClass.error("Vous n'avez pas les droits nécessaires pour créer une UE", status_code=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        return ApiResponseClass.error(f"Une erreur inattendue s'est produite: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def UpdateUEAndPrerequisites(request, ue_id):
    try:
        ue = get_object_or_404(UE, id=ue_id)

        # Mettre à jour les informations de l'UE
        serializer = UESerializer(ue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

        # Vérifier si les prérequis sont fournis dans la requête
        if 'prerequisites' in request.data:
            prerequisites_data = request.data.get('prerequisites', [])
            # Effacer les prérequis actuels
            ue.prerequisites.clear()

            # Traiter chaque prérequis
            for prereq_data in prerequisites_data:
                if isinstance(prereq_data, dict) and 'ueId' in prereq_data:
                    prereq_id = prereq_data['ueId']
                    try:
                        prereq_ue = UE.objects.get(id=prereq_id)
                        # Vérifier que le cycle du prérequis est inférieur ou égal à celui de l'UE
                        if prereq_ue.cycle <= ue.cycle:
                            ue.prerequisites.add(prereq_ue)
                        else:
                            return ApiResponseClass.error(f"Le prérequis {prereq_ue.name} est d'un cycle supérieur à l'UE.")

                    except UE.DoesNotExist:
                        return ApiResponseClass.error(f"Le prérequis {prereq_id} n'existe pas.")
                else:
                    return ApiResponseClass.error(f"Le format des prérequis est invalide.")  # Ignorer les entrées mal formatées

        updated_ue = UE.objects.get(id=ue_id)
        serializer = UESerializer(updated_ue)

        return ApiResponseClass.success("l'UE et ses prérequis ont été mis à jour avec succès", serializer.data)

    except Exception as e:
        return ApiResponseClass.error(f"Une erreur s'est produite lors de la mise à jour de l'UE et des prérequis: {str(e)}")

@api_view(['DELETE'])
def DeleteUE(request, ue_id):
    try:
        ue = get_object_or_404(UE, id=ue_id)
        
        # Changer isActive à False au lieu de supprimer l'objet
        ue.isActive = False
        ue.save()
        
        return ApiResponseClass.success("UE désactivée avec succès", {"ueId": ue.id})
    
    except Exception as e:
        return ApiResponseClass.error(f"Une erreur s'est produite lors de la désactivation de l'UE: {str(e)}")

