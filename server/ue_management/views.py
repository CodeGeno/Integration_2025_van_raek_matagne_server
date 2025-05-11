# server/ue_management/views.py
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from datetime import datetime, timedelta

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from security.entities.accountTypeEnum import AccountRoleEnum
from security.models import Student
from ue_management.models import Lesson, AcademicUE, Result
from ue_management.serializers import LessonSerializer, AcademicUESerializer, ResultSerializer
from ue.models import UE
from section.models import Section
from section.serializers import SectionSerializer

from api.models import ApiResponseClass


class AcademicUEListView(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Liste toutes les UEs académiques",
        manual_parameters=[
            openapi.Parameter(
                'section_id',
                openapi.IN_QUERY,
                description="ID de la section pour filtrer les UEs",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'name',
                openapi.IN_QUERY,
                description="Nom de l'UE pour filtrer",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'cycle',
                openapi.IN_QUERY,
                description="Cycle pour filtrer les UEs",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'year',
                openapi.IN_QUERY,
                description="Année pour filtrer les UEs",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'active_only',
                openapi.IN_QUERY,
                description="Filtrer uniquement les UEs actives",
                type=openapi.TYPE_BOOLEAN,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Liste des UEs académiques récupérée avec succès",
                schema=AcademicUESerializer(many=True)
            )
        }
    )
    def get(self, request):
        try:
            section_id = request.query_params.get('section_id')
            name = request.query_params.get('name')
            cycle = request.query_params.get('cycle')
            year = request.query_params.get('year')
            active_only = request.query_params.get('active_only')
            
            academic_ues = AcademicUE.objects.all()
            
            if section_id:
                try:
                    section_id = int(section_id)
                    academic_ues = academic_ues.filter(ue__section_id=section_id)
                except ValueError:
                    return ApiResponseClass.error(
                        "L'ID de la section doit être un nombre entier",
                        status.HTTP_400_BAD_REQUEST
                    )
            
            if name:
                academic_ues = academic_ues.filter(ue__name__icontains=name)
                
            if cycle:
                try:
                    cycle = int(cycle)
                    academic_ues = academic_ues.filter(ue__cycle=cycle)
                except ValueError:
                    return ApiResponseClass.error(
                        "Le cycle doit être un nombre entier",
                        status.HTTP_400_BAD_REQUEST
                    )

            if year:
                try:
                    year = int(year)
                    academic_ues = academic_ues.filter(year=year)
                except ValueError:
                    return ApiResponseClass.error(
                        "L'année doit être un nombre entier",
                        status.HTTP_400_BAD_REQUEST
                    )
                    
            if active_only and active_only.lower() == 'true':
                academic_ues = academic_ues.filter(ue__isActive=True)
                
            serializer = AcademicUESerializer(academic_ues, many=True)
            return ApiResponseClass.success("Liste des UEs académiques récupérée avec succès", serializer.data)
        except Exception as e:
            return ApiResponseClass.error(
                f"Erreur lors de la récupération des UEs académiques: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Crée une nouvelle UE académique",
        request_body=AcademicUESerializer,
        responses={
            201: openapi.Response(
                description="UE académique créée avec succès",
                schema=AcademicUESerializer()
            ),
            400: openapi.Response(description="Données invalides")
        }
    )
    def post(self, request):
        try:
            serializer = AcademicUESerializer(data=request.data)
            if serializer.is_valid():

                serializer.save()
                return ApiResponseClass.created("UE académique créée avec succès", serializer.data)
            return ApiResponseClass.error(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la création de l'UE académique: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateNextYearUEsView(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Génère les UE académiques pour l'année suivante",
        responses={
            201: openapi.Response(
                description="UEs académiques générées avec succès",
                schema=AcademicUESerializer(many=True)
            ),
            400: openapi.Response(description="Erreur lors de la génération")
        }
    )
    def post(self, request):
        try:
            # Récupérer l'année actuelle
            current_year = datetime.now().year
            next_year = current_year + 1

            # Récupérer toutes les UE actives
            active_ues = UE.objects.filter(isActive=True)

            # Calculer les dates de début et de fin pour l'année suivante
            start_date = datetime(next_year, 9, 15)  # 15 septembre
            end_date = datetime(next_year, 6, 30)    # 30 juin

            created_ues = []
            for ue in active_ues:
                # Vérifier si l'UE académique existe déjà pour l'année suivante
                if not AcademicUE.objects.filter(ue=ue, year=next_year).exists():
                    academic_ue = AcademicUE.objects.create(
                        year=next_year,
                        start_date=start_date,
                        end_date=end_date,
                        ue=ue
                    )
                    created_ues.append(academic_ue)

            serializer = AcademicUESerializer(created_ues, many=True)
            return ApiResponseClass.created(
                f"{len(created_ues)} UEs académiques générées avec succès pour l'année {next_year}",
                serializer.data
            )

        except Exception as e:
            return ApiResponseClass.error(
                f"Erreur lors de la génération des UEs académiques: {str(e)}",
                status.HTTP_400_BAD_REQUEST
            )


class AcademicUEDetailView(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Récupère une UE académique par ID",
        responses={
            200: openapi.Response(
                description="UE académique récupérée avec succès",
                schema=AcademicUESerializer()
            ),
            404: openapi.Response(description="UE académique non trouvée")
        }
    )
    def get(self, request, pk):
        academic_ue = get_object_or_404(AcademicUE, pk=pk)
        serializer = AcademicUESerializer(academic_ue)
        return ApiResponseClass.success("UE académique récupérée avec succès", serializer.data)

    @swagger_auto_schema(
        operation_description="Met à jour une UE académique existante",
        request_body=AcademicUESerializer,
        responses={
            200: openapi.Response(
                description="UE académique mise à jour avec succès",
                schema=AcademicUESerializer()
            ),
            400: openapi.Response(description="Données invalides"),
            404: openapi.Response(description="UE académique non trouvée")
        }
    )
    def patch(self, request, pk):
        academic_ue = get_object_or_404(AcademicUE, pk=pk)
        serializer = AcademicUESerializer(academic_ue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ApiResponseClass.success("UE académique mise à jour avec succès", serializer.data)
        return ApiResponseClass.error(serializer.errors, status.HTTP_400_BAD_REQUEST)


class LessonListView(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Liste toutes les séances",
        responses={
            200: openapi.Response(
                description="Liste des séances récupérée avec succès",
                schema=LessonSerializer(many=True)
            )
        }
    )
    def get(self, request):
        lessons = Lesson.objects.all()
        serializer = LessonSerializer(lessons, many=True)
        return ApiResponseClass.success("Liste des séances récupérée avec succès", serializer.data)

    @swagger_auto_schema(
        operation_description="Crée une nouvelle séance",
        request_body=LessonSerializer,
        responses={
            201: openapi.Response(
                description="Séance créée avec succès",
                schema=LessonSerializer()
            ),
            400: openapi.Response(description="Données invalides")
        }
    )
    def post(self, request):
        serializer = LessonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ApiResponseClass.created("Séance créée avec succès", serializer.data)
        return ApiResponseClass.error("Données invalides", serializer.errors)


class LessonDetailView(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Récupère une séance par ID",
        responses={
            200: openapi.Response(
                description="Séance récupérée avec succès",
                schema=LessonSerializer()
            ),
            404: openapi.Response(description="Séance non trouvée")
        }
    )
    def get(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)
        serializer = LessonSerializer(lesson)
        return ApiResponseClass.success("Séance récupérée avec succès", serializer.data)

    @swagger_auto_schema(
        operation_description="Met à jour une séance existante",
        request_body=LessonSerializer,
        responses={
            200: openapi.Response(
                description="Séance mise à jour avec succès",
                schema=LessonSerializer()
            ),
            400: openapi.Response(description="Données invalides"),
            404: openapi.Response(description="Séance non trouvée")
        }
    )
    def patch(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)
        serializer = LessonSerializer(lesson, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ApiResponseClass.success("Séance mise à jour avec succès", serializer.data)
        return ApiResponseClass.error(serializer.errors, status.HTTP_400_BAD_REQUEST)


class ResultListView(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Liste tous les résultats",
        responses={
            200: openapi.Response(
                description="Liste des résultats récupérée avec succès",
                schema=ResultSerializer(many=True)
            )
        }
    )
    def get(self, request):
        results = Result.objects.all()
        serializer = ResultSerializer(results, many=True)
        return ApiResponseClass.success("Liste des résultats récupérée avec succès", serializer.data)

    @swagger_auto_schema(
        operation_description="Crée un nouveau résultat",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['academicsueId', 'result', 'period', 'studentid', 'success'],
            properties={
                'academicsueId': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID de l\'UE académique'),
                'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='Résultat obtenu'),
                'period': openapi.Schema(type=openapi.TYPE_INTEGER, description='Nombre de périodes'),
                'studentid': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID de l\'étudiant'),
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Succès ou échec'),
                'isexempt': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Est dispensé', default=False)
            }
        ),
        responses={
            201: openapi.Response(
                description="Résultat créé avec succès",
                schema=ResultSerializer()
            ),
            400: openapi.Response(description="Données invalides ou résultat hors limites"),
            500: openapi.Response(description="Erreur serveur")
        }
    )
    def post(self, request):
        #@has_employee_role([AccountRoleEnum.ADMINISTRATOR])
        def create_result(request):
            try:
                # Validation des règles métier
                result_value = request.data.get('result')
                period_value = request.data.get('period')

                # Vérifier que result est dans la plage valide (period * 10)
                if period_value and result_value:
                    max_result = period_value * 10
                    min_result = max_result / 2  # 50% pour réussir

                    if not (min_result <= result_value <= max_result):
                        return ApiResponseClass.error(
                            f"Le résultat doit être entre {min_result} et {max_result} pour {period_value} périodes",
                            status_code=status.HTTP_400_BAD_REQUEST
                        )

                serializer = ResultSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return ApiResponseClass.created("Résultat créé avec succès", serializer.data)
                return ApiResponseClass.error(serializer.errors, status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return ApiResponseClass.error(f"Erreur lors de la création: {str(e)}",
                                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return create_result(request)


class ResultDetailView(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Récupère un résultat par ID",
        responses={
            200: openapi.Response(
                description="Résultat récupéré avec succès",
                schema=ResultSerializer()
            ),
            404: openapi.Response(description="Résultat non trouvé")
        }
    )
    def get(self, request, pk):
        result = get_object_or_404(Result, pk=pk)
        serializer = ResultSerializer(result)
        return ApiResponseClass.success("Résultat récupéré avec succès", serializer.data)

    @swagger_auto_schema(
        operation_description="Met à jour un résultat existant",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'result': openapi.Schema(type=openapi.TYPE_INTEGER, description='Résultat obtenu'),
                'period': openapi.Schema(type=openapi.TYPE_INTEGER, description='Nombre de périodes'),
                'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Succès ou échec'),
                'isexempt': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Est dispensé'),
                'approved': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Est approuvé')
            }
        ),
        responses={
            200: openapi.Response(
                description="Résultat mis à jour avec succès",
                schema=ResultSerializer()
            ),
            400: openapi.Response(description="Données invalides ou résultat hors limites"),
            403: openapi.Response(description="Résultat déjà approuvé, modification impossible"),
            404: openapi.Response(description="Résultat non trouvé"),
            500: openapi.Response(description="Erreur serveur")
        }
    )
    def patch(self, request, pk):
        #@has_employee_role([AccountRoleEnum.ADMINISTRATOR])
        def update_result(request, pk):
            try:
                result = get_object_or_404(Result, pk=pk)

                # Si on essaie de modifier un résultat approuvé (sauf pour l'approbation elle-même)
                if result.approved and not request.data.get('approved') and any(key in request.data for key in ['result', 'period', 'success', 'isexempt']):
                    return ApiResponseClass.error(
                        "Ce résultat a déjà été approuvé et ne peut être modifié",
                        status_code=status.HTTP_403_FORBIDDEN
                    )

                # Si on essaie d'approuver un résultat, on vérifie qu'il a un résultat valide
                if request.data.get('approved') and not result.isExempt and not result.result:
                    return ApiResponseClass.error(
                        "Un résultat doit avoir une note valide avant d'être approuvé",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                result_value = request.data.get('result')
                period_value = request.data.get('period', result.period)

                if result_value:
                    max_result = period_value * 10
                    min_result = max_result / 2

                    if not (min_result <= result_value <= max_result):
                        return ApiResponseClass.error(
                            f"Le résultat doit être entre {min_result} et {max_result} pour {period_value} périodes",
                            status_code=status.HTTP_400_BAD_REQUEST
                        )
                    
                    # Mise à jour automatique du champ success
                    request.data['success'] = result_value >= min_result

                serializer = ResultSerializer(result, data=request.data, partial=True)
                if serializer.is_valid():
                    updated_result = serializer.save()
                    return ApiResponseClass.success("Résultat mis à jour avec succès", serializer.data)
                return ApiResponseClass.error(serializer.errors, status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return ApiResponseClass.error(f"Erreur lors de la mise à jour: {str(e)}",
                                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return update_result(request, pk)

@api_view(['GET'])
def AcademicUEGetById(request, id):
    try:
        academicUE = AcademicUE.objects.select_related('professor').prefetch_related('students','lessons','results').get(id=id)
        serializer = AcademicUESerializer(academicUE)
        return ApiResponseClass.success("Détails de l'UE académique récupérés avec succès", serializer.data)
    except AcademicUE.DoesNotExist:
        return ApiResponseClass.error("UE académique non trouvée", status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ApiResponseClass.error(f"Erreur lors de la récupération de l'UE académique: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def SectionRegistration(request, id):
 
    
    try:
        section = Section.objects.get(id=id)
        serializer = SectionSerializer(section)
        return ApiResponseClass.success("Détails de la section récupérés avec succès", serializer.data)
    except Section.DoesNotExist:
        return ApiResponseClass.error("Section non trouvée", status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ApiResponseClass.error(f"Erreur lors de la récupération de la section: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def RegisterStudentsToAcademicUE(request, id):
    try:
        academic_ue = get_object_or_404(AcademicUE, id=id)
        student_ids = request.data.get('student_ids', [])
        
        if not student_ids:
            return ApiResponseClass.error("Aucun étudiant spécifié", status.HTTP_400_BAD_REQUEST)
            
        # Ajouter les étudiants à l'UE académique
        academic_ue.students.add(*student_ids)
        
        # Créer les résultats pour chaque étudiant
        for student_id in student_ids:
            # Vérifier si un résultat existe déjà
            if not Result.objects.filter(academicsUE=academic_ue, student_id=student_id).exists():
                Result.objects.create(
                    academicsUE=academic_ue,
                    student_id=student_id,
                    period=academic_ue.ue.period,
                    result=None,
                    success=False,
                    isExempt=False,
                    approved=False
                )
        
        serializer = AcademicUESerializer(academic_ue)
        return ApiResponseClass.success("Étudiants inscrits avec succès", serializer.data)
    except Exception as e:
        return ApiResponseClass.error(f"Erreur lors de l'inscription des étudiants: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def GetStudentResults(request, academic_ue, student):
    """
    Récupère les résultats d'un étudiant pour une UE académique spécifique.
    """
    try:
        # Validation des paramètres
        academic_ue_id = int(academic_ue)
        student_id = int(student)

        # Récupération des résultats
        results = Result.objects.filter(
            academicsUE_id=academic_ue_id,
            student_id=student_id
        ).order_by('-id')  # Tri par ID décroissant pour avoir les plus récents en premier

        serializer = ResultSerializer(results, many=True)
        return ApiResponseClass.success(
            "Résultats récupérés avec succès",
            serializer.data
        )
    except ValueError:
        return ApiResponseClass.error(
            "Les IDs doivent être des nombres entiers",
            status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return ApiResponseClass.error(
            f"Erreur lors de la récupération des résultats: {str(e)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def GetStudentAcademicUEs(request, student_id):
    try:
        # Récupérer l'étudiant
        student = get_object_or_404(Student, id=student_id)
        
        # Récupérer toutes les UE académiques de l'étudiant
        academic_ues = AcademicUE.objects.filter(students=student)
        
        # Sérialiser les données
        serializer = AcademicUESerializer(academic_ues, many=True)
        
        return ApiResponseClass.success(
            "UE académiques de l'étudiant récupérées avec succès",
            serializer.data
        )
    except Exception as e:
        return ApiResponseClass.error(
            f"Erreur lors de la récupération des UE académiques: {str(e)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )     