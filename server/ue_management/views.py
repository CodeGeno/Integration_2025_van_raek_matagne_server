# server/ue_management/views.py
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from datetime import datetime, timedelta
from django.db.models import Q
from attendance.models import Attendance, AttendanceStatusEnum
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from security.entities.accountTypeEnum import AccountRoleEnum
from ue_management.models import Lesson, AcademicUE, Result
from ue_management.serializers import LessonSerializer, AcademicUESerializer, ResultSerializer,StudentAcademicUeRegistrationSerializer
from ue.models import UE
from section.models import Section
from section.serializers import SectionSerializer
from security.models import Student
from api.models import ApiResponseClass
from security.serializers import StudentSerializer
from ue_management.models import StudentAcademicUeRegistrationStatus
class AcademicUEListView(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Liste toutes les UEs académiques",
        responses={
            200: openapi.Response(
                description="Liste des UEs académiques récupérée avec succès",
                schema=AcademicUESerializer(many=True)
            )
        }
    )
    def get(self, request):
        academic_ues = AcademicUE.objects.all()
        serializer = AcademicUESerializer(academic_ues, many=True)
        return ApiResponseClass.success("Liste des UEs académiques récupérée avec succès", serializer.data)

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
                'isexempt': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Est dispensé')
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
        @has_employee_role([AccountRoleEnum.ADMINISTRATOR])
        def update_result(request, pk):
            try:
                result = get_object_or_404(Result, pk=pk)

                if hasattr(result, 'approved') and result.approved:
                    return ApiResponseClass.error(
                        "Ce résultat a déjà été approuvé et ne peut être modifié",
                        status_code=status.HTTP_403_FORBIDDEN
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
def SectionRegistration(request):   
    try:
        # Vérification des données requises
        required_fields = ['studentId', 'sectionId', 'cycle']
        missing_fields = [field for field in required_fields if not request.data.get(field)]
        if missing_fields:
            return ApiResponseClass.error(
                f"Champs manquants dans la requête : {', '.join(missing_fields)}",
                status.HTTP_400_BAD_REQUEST
            )

        try:
            student = get_object_or_404(Student, id=request.data.get('studentId'))
        except Student.DoesNotExist:
            return ApiResponseClass.error(
                f"Étudiant avec l'ID {request.data.get('studentId')} non trouvé",
                status.HTTP_404_NOT_FOUND
            )

        try:
            section = get_object_or_404(Section, id=request.data.get('sectionId'))
        except Section.DoesNotExist:
            return ApiResponseClass.error(
                f"Section avec l'ID {request.data.get('sectionId')} non trouvée",
                status.HTTP_404_NOT_FOUND
            )

        cycle = request.data.get('cycle')
        year = datetime.now().year

        try:
            # Récupérer toutes les UEs de la section pour le cycle spécifié
            ues = section.ues.filter(cycle=cycle)
            
            if not ues.exists():
                return ApiResponseClass.error(
                    f"Aucune UE trouvée pour le cycle {cycle}",
                    status.HTTP_404_NOT_FOUND
                )

            # Liste pour stocker les résultats de validation
            validation_results = []
            already_registered_ues = []

            for ue in ues:
                # Récupérer l'UE académique pour l'année en cours
                academic_ue = ue.academic_ues.filter(year=year).first()
                
                if not academic_ue:
                    validation_results.append({
                        'ue_name': ue.name,
                        'has_all_prerequisites': False,
                        'missing_prerequisites': ['UE académique non disponible pour cette année'],
                        'status': 'non_disponible'
                    })
                    continue

                # Vérifier si l'étudiant est déjà inscrit
                if academic_ue.students.filter(id=student.id).exists():
                    already_registered_ues.append(ue.name)
                    validation_results.append({
                        'ue_name': ue.name,
                        'has_all_prerequisites': True,
                        'missing_prerequisites': [],
                        'status': 'deja_inscrit'
                    })
                    continue

                has_all_prerequisites = True
                missing_prerequisites = []
                
                if ue.prerequisites.exists():
                    for prerequisite in ue.prerequisites.all():
                        try:
                            # Vérifier si l'étudiant a un résultat pour ce prérequis
                            has_result = Result.objects.filter(
                                academicsUE__ue=prerequisite,
                                student=student,
                                success=True
                            ).exists()
                            
                            if not has_result:
                                has_all_prerequisites = False
                                missing_prerequisites.append(prerequisite.name)
                        except Exception as e:
                            return ApiResponseClass.error(
                                f"Erreur lors de la vérification du prérequis {prerequisite.name}: {str(e)}",
                                status.HTTP_500_INTERNAL_SERVER_ERROR
                            )
                
                validation_results.append({
                    'ue_name': ue.name,
                    'has_all_prerequisites': has_all_prerequisites,
                    'missing_prerequisites': missing_prerequisites,
                    'status': 'inscription_reussie' if has_all_prerequisites else 'prerequis_manquants'
                })
                
                if has_all_prerequisites:
                    try:
                        academic_ue.students.add(student)
                    except Exception as e:
                        return ApiResponseClass.error(
                            f"Erreur lors de l'inscription à l'UE {ue.name}: {str(e)}",
                            status.HTTP_500_INTERNAL_SERVER_ERROR
                        )

            # Préparer le message de réponse
            message = "Inscription aux UEs de la section effectuée avec succès"
            if already_registered_ues:
                message += f". L'étudiant était déjà inscrit aux UEs suivantes : {', '.join(already_registered_ues)}"

            serializer = SectionSerializer(section)
            return ApiResponseClass.success(
                message,
                {
                    'section': serializer.data,
                    'validation_results': validation_results
                }
            )

        except Exception as e:
            return ApiResponseClass.error(
                f"Erreur lors du traitement des UEs académiques: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    except Exception as e:
        return ApiResponseClass.error(
            f"Erreur inattendue lors de l'inscription à la section: {str(e)}",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def StudentAcademicUeRegistration(request, academicUeId, studentId):
    try:
        # Vérification de l'existence de l'UE académique et de l'étudiant
        student = get_object_or_404(Student, id=studentId)
        academic_ue = get_object_or_404(AcademicUE, id=academicUeId)
        
        # Vérification des prérequis
        has_all_prerequisites = True
        if academic_ue.ue.prerequisites.exists():
            for prerequisite in academic_ue.ue.prerequisites.all():
                # Vérifier si l'étudiant a un résultat pour ce prérequis
                has_result = Result.objects.filter(
                    academicsUE__ue=prerequisite,
                    student=student,
                    success=True
                ).exists()
                
                if not has_result:
                    has_all_prerequisites = False
                    break

        # Si l'étudiant a tous les prérequis, l'inscrire dans l'UE académique
        if has_all_prerequisites:
            academic_ue.students.add(student)
            return ApiResponseClass.created(
                "Inscription réussie - L'étudiant a été inscrit à l'UE académique",
                {"student_id": student.id, "academic_ue_id": academic_ue.id}
            )
        else:
            return ApiResponseClass.error(
                "L'étudiant n'a pas tous les prérequis nécessaires pour s'inscrire à cette UE",
                status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return ApiResponseClass.error(f"Erreur lors de l'inscription: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

      
        
@api_view(['GET'])
def StudentStatusGetByAcademicUeId(request, academicUeId):
    try:
        # Récupération des paramètres de filtrage
        search = request.query_params.get('search', '')
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 25)), 25)  # Maximum 25 éléments par page

        # Vérification de l'existence de l'UE académique
        academic_ue = get_object_or_404(AcademicUE, id=academicUeId)

        # Construction de la requête de base en excluant les étudiants déjà inscrits
        query = Student.objects.exclude(enrolled_ues=academic_ue)
        
        # Application du filtre de recherche
        if search:
            query = query.filter(
                Q(contactDetails__firstName__icontains=search) |
                Q(contactDetails__lastName__icontains=search) |
                Q(identifier__icontains=search) |
                Q(email__icontains=search)
            )

        # Calcul de la pagination
        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        # Récupération des résultats paginés
        total_count = query.count()
        students = query[start_index:end_index]
        
        # Préparation des données des étudiants avec leur statut
        student_data = []
        for student in students:
            status = StudentAcademicUeRegistrationStatus.AP.value  # Par défaut, on considère que l'étudiant a tous les prérequis
            
            # Vérification des prérequis
            if academic_ue.ue.prerequisites.exists():
                for prerequisite in academic_ue.ue.prerequisites.all():
                    # Vérifier si l'étudiant a un résultat pour ce prérequis
                    has_result = Result.objects.filter(
                        academicsUE__ue=prerequisite,
                        student=student,
                        success=True
                    ).exists()
                    
                    if not has_result:
                        status = StudentAcademicUeRegistrationStatus.NP.value
                        break

            # Ajout des données de l'étudiant avec son statut
            student_serializer = StudentAcademicUeRegistrationSerializer(student)
            student_dict = student_serializer.data
            student_dict['status'] = status
            student_data.append(student_dict)

        return ApiResponseClass.success("Détails des états des étudiants récupérés avec succès", student_data)
    except Student.DoesNotExist:
        return ApiResponseClass.error("Étudiants non trouvés", status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return ApiResponseClass.error(f"Erreur lors de la récupération des états des étudiants: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def RegisterStudentsToAcademicUE(request, id):
    try:
        academic_ue = get_object_or_404(AcademicUE, id=id)
        student_ids = request.data.get('student_ids', [])

        if not student_ids:
            return ApiResponseClass.error("Aucun étudiant spécifié", status.HTTP_400_BAD_REQUEST)

        registered_students = []
        failed_students = []

        for student_id in student_ids:
            try:
                student = Student.objects.get(id=student_id)
                
                # Vérification des prérequis
                has_all_prerequisites = True
                if academic_ue.ue.prerequisites.exists():
                    for prerequisite in academic_ue.ue.prerequisites.all():
                        has_result = Result.objects.filter(
                            academicsUE__ue=prerequisite,
                            student=student,
                            success=True
                        ).exists()
                        
                        if not has_result:
                            has_all_prerequisites = False
                            break

                if has_all_prerequisites:
                    academic_ue.students.add(student)
                    registered_students.append(student_id)
                else:
                    failed_students.append(student_id)

            except Student.DoesNotExist:
                failed_students.append(student_id)

        return ApiResponseClass.success(
            "Inscription des étudiants terminée",
            {
                "registered_students": registered_students,
                "failed_students": failed_students
            }
        )

    except Exception as e:
        return ApiResponseClass.error(f"Erreur lors de l'inscription des étudiants: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def GetStudentResults(request, academic_ue, student):
    try:
        results = Result.objects.filter(
            academicsUE_id=academic_ue,
            student_id=student
        )
        
        if not results.exists():
            return ApiResponseClass.error("Aucun résultat trouvé", status.HTTP_404_NOT_FOUND)

        serializer = ResultSerializer(results, many=True)
        return ApiResponseClass.success("Résultats récupérés avec succès", serializer.data)

    except Exception as e:
        return ApiResponseClass.error(f"Erreur lors de la récupération des résultats: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)     