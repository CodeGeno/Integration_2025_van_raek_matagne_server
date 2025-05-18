from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Section, SectionCategory
from .serializers import SectionSerializer, SectionCreationSerializer
from api.models import ApiResponseClass
from django.db.models import Q
from api.pagination import StandardResultsSetPagination
from security.decorators import checkRoleToken
from security.models import AccountRoleEnum
# Create your views here.

class SectionCreationView(APIView):
    @checkRoleToken([AccountRoleEnum.ADMINISTRATOR])
    def post(self, request):
        try:
            serializer = SectionCreationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ApiResponseClass.created("Section créée avec succès", serializer.data)
            return ApiResponseClass.error("Erreur lors de la création de la section", serializer.errors)
        except ValueError as e:
            return ApiResponseClass.error(f"Erreur de valeur: {str(e)}", status.HTTP_400_BAD_REQUEST)
        except TypeError as e:
            return ApiResponseClass.error(f"Erreur de type: {str(e)}", status.HTTP_400_BAD_REQUEST)
        except Section.DoesNotExist:
            return ApiResponseClass.error("La section demandée n'existe pas", status.HTTP_404_NOT_FOUND)
        except PermissionError:
            return ApiResponseClass.error("Vous n'avez pas les droits nécessaires pour créer une section", status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return ApiResponseClass.error(f"Une erreur inattendue s'est produite: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetAllSectionsView(APIView):
    @checkRoleToken([AccountRoleEnum.EDUCATOR,AccountRoleEnum.PROFESSOR,AccountRoleEnum.ADMINISTRATOR])
    def get(self, request):
        try:
            # Récupérer toutes les sections actives
            sections = Section.objects.filter(isActive=True).order_by('id')
            
            # Recherche par nom, type ou catégorie
            search_query = request.query_params.get('search', "")
            type_query = request.query_params.get('type', "")
            category_query = request.query_params.get('category', "")

            # Appliquer les filtres séparément et seulement si nécessaire
            if search_query:
                sections = sections.filter(name__icontains=search_query)
            
            if type_query:
                # Filtrer directement sur le nom d'énumération
                sections = sections.filter(sectionType=type_query)
                
            if category_query:
                # Filtrer directement sur le nom d'énumération
                sections = sections.filter(sectionCategory=category_query)
            
            # Pagination
            paginator = StandardResultsSetPagination()
            paginated_sections = paginator.paginate_queryset(sections, request)
            serializer = SectionSerializer(paginated_sections, many=True)
            
            # Retourner la réponse avec les informations de pagination
            return ApiResponseClass.succesOverview(
                "Liste des sections récupérée avec succès",
                serializer.data,
                paginator.page.number,
                paginator.page.paginator.num_pages
            )
        except Exception as e:
            return ApiResponseClass.error(f"Une erreur s'est produite lors de la récupération des sections: {str(e)}")


class DeleteSectionView(APIView):
    @checkRoleToken([AccountRoleEnum.ADMINISTRATOR])
    def delete(self, request, section_id):
        try:
            # Récupérer la section par son ID
            section = get_object_or_404(Section, id=section_id)
            
            # Mettre à jour le champ isActive au lieu de supprimer
            section.isActive = False
            section.save()
            
            # Sérialiser la section mise à jour pour la réponse
            serializer = SectionSerializer(section)
            
            return ApiResponseClass.success("Section désactivée avec succès", serializer.data)
        except Exception as e:
            return ApiResponseClass.error(f"Une erreur s'est produite lors de la désactivation de la section: {str(e)}")


class UpdateSectionView(APIView):
    @checkRoleToken([AccountRoleEnum.ADMINISTRATOR])
    def patch(self, request, section_id):
        try:
            # Récupérer la section par son ID
            section = get_object_or_404(Section, id=section_id, isActive=True)
            
            # Afficher les données reçues pour le débogage
            serializer = SectionSerializer(section, data=request.data, partial=True)

            if serializer.is_valid():
                section = serializer.save()
                return ApiResponseClass.success("Section mise à jour avec succès", serializer.data)
            
            return ApiResponseClass.error(f"Erreur lors de la mise à jour de la section: {serializer.errors}")
        except Section.DoesNotExist:
            return ApiResponseClass.error("La section demandée n'existe pas ou est désactivée", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return ApiResponseClass.error(f"Une erreur s'est produite lors de la mise à jour de la section: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetSectionByIdView(APIView):
    def get(self, request, section_id):
        try:
            # Récupérer la section par son ID
            section = get_object_or_404(Section, id=section_id, isActive=True)
            
            # Sérialiser la section pour la réponse
            serializer = SectionSerializer(section)
            
            return ApiResponseClass.success("Section récupérée avec succès", serializer.data)
        except Section.DoesNotExist:
            return ApiResponseClass.error("La section demandée n'existe pas ou est désactivée", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return ApiResponseClass.error(f"Une erreur s'est produite lors de la récupération de la section: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    
