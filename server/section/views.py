from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Section
from .serializers import SectionSerializer
from api.models import ApiResponseClass
# Create your views here.

@api_view(['POST'])
def SectionCreation(request):
    try:
        serializer = SectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ApiResponseClass.created("Section créée avec succès", serializer.data)
        return ApiResponseClass.error("Erreur lors de la création de la section", serializer.errors)
    except Exception as e:
        return ApiResponseClass.error(f"Une erreur inattendue s'est produite: {str(e)}")


@api_view(['GET'])
def GetAllSections(request):
    try:
        sections = Section.objects.filter(isActive=True)
        serializer = SectionSerializer(sections, many=True)
        return ApiResponseClass.success("Liste des sections actives récupérée avec succès", serializer.data)
    except Exception as e:
        return ApiResponseClass.error(f"Une erreur s'est produite lors de la récupération des sections: {str(e)}")


@api_view(['DELETE'])
def DeleteSection(request, section_id):
    try:
        # Récupérer la section par son ID
        section = get_object_or_404(Section, sectionId=section_id)
        
        # Mettre à jour le champ isActive au lieu de supprimer
        section.isActive = False
        section.save()
        
        # Sérialiser la section mise à jour pour la réponse
        serializer = SectionSerializer(section)
        
        return ApiResponseClass.success("Section désactivée avec succès", serializer.data)
    except Exception as e:
        return ApiResponseClass.error(f"Une erreur s'est produite lors de la désactivation de la section: {str(e)}")


    
