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
from security.entities.accountTypeEnum import AccountRoleEnum
from security.models import Student
from security.decorators import jwt_required, checkRoleToken
from security.serializers import StudentSerializer
from ue_management.models import Lesson, AcademicUE, Result, StudentAcademicUeRegistrationStatus,LessonStatus
from ue_management.serializers import AcademicUEDetailsSerializer, LessonSerializer, AcademicUESerializer, ResultSerializer, StudentAcademicUeRegistrationSerializer
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
    @checkRoleToken([AccountRoleEnum.EDUCATOR,AccountRoleEnum.PROFESSOR,AccountRoleEnum.ADMINISTRATOR])
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
        
            if(request.user.role==AccountRoleEnum.PROFESSOR.name):
                academic_ues = academic_ues.filter(professor_id=request.user.id)

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
    @checkRoleToken()
    def post(self, request):
        
        try:
            serializer = AcademicUESerializer(data=request.data)
            if serializer.is_valid():

                serializer.save()
                return ApiResponseClass.created("UE académique créée avec succès", serializer.data)
            return ApiResponseClass.error(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la création de l'UE académique: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)




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
        try:
            academic_ue = get_object_or_404(AcademicUE, pk=pk)
            serializer = AcademicUESerializer(academic_ue)
            return ApiResponseClass.success("UE académique récupérée avec succès", serializer.data)
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la récupération de l'UE académique: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    @checkRoleToken([AccountRoleEnum.EDUCATOR,AccountRoleEnum.PROFESSOR])
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
        try:
            lessons = Lesson.objects.all()
            serializer = LessonSerializer(lessons, many=True)
            return ApiResponseClass.success("Liste des séances récupérée avec succès", serializer.data)
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la récupération des séances: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        try:
            lesson = get_object_or_404(Lesson, pk=pk)
            serializer = LessonSerializer(lesson)
            return ApiResponseClass.success("Séance récupérée avec succès", serializer.data)
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la récupération de la séance: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Met à jour une séance existante",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'lesson_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE, description='Date de la séance'),
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='Statut de la séance', enum=[status.value for status in LessonStatus])
            }
        ),
        responses={
            200: openapi.Response(
                description="Séance mise à jour avec succès",
                schema=LessonSerializer()
            ),
            400: openapi.Response(description="Données invalides"),
            404: openapi.Response(description="Séance non trouvée")
        }
    )
    @checkRoleToken([AccountRoleEnum.EDUCATOR, AccountRoleEnum.PROFESSOR])
    def patch(self, request, pk):
        try:
            lesson = get_object_or_404(Lesson, pk=pk)
            serializer = LessonSerializer(lesson, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return ApiResponseClass.success("Séance mise à jour avec succès", serializer.data)
            return ApiResponseClass.error(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ApiResponseClass.error(
                f"Erreur lors de la mise à jour de la séance: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
        try:
            results = Result.objects.all()
            serializer = ResultSerializer(results, many=True)
            return ApiResponseClass.success("Liste des résultats récupérée avec succès", serializer.data)
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la récupération des résultats: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        def create_result(request):
            try:
                # Validation des données requises
                studentid = request.data.get('studentid')
                academicsueId = request.data.get('academicsueId')
                result_value = request.data.get('result')
                period_value = request.data.get('period')
                isExempt=request.data.get('isexempt', False)
                # Vérification que les données nécessaires sont présentes
                
                # Vérification de l'existence de l'étudiant
                try:
                    student = Student.objects.get(id=studentid)
                except Student.DoesNotExist:
                    return ApiResponseClass.error(
                        f"Étudiant avec l'ID {studentid} non trouvé",
                        status.HTTP_404_NOT_FOUND
                    )
                
                # Vérification de l'existence de l'UE académique
                try:
                    academic_ue = AcademicUE.objects.get(id=academicsueId)
                except AcademicUE.DoesNotExist:
                    return ApiResponseClass.error(
                        f"UE académique avec l'ID {academicsueId} non trouvée",
                        status.HTTP_404_NOT_FOUND
                    )

                # Vérifier que result est dans la plage valide (period * 10)
                max_result = period_value * 10
                min_result = max_result / 2  # 50% pour réussir
                
                if not isExempt:
                    if not (min_result <= result_value <= max_result):
                        return ApiResponseClass.error(
                            f"Le résultat doit être entre {min_result} et {max_result} ",
                            status.HTTP_400_BAD_REQUEST
                        )
                
                # Déterminer si l'étudiant a réussi (success = True si result >= min_result)
                is_success = True
                if not isExempt and result_value is not None:
                    is_success = result_value >= min_result
                
                # Création du résultat
                result = Result.objects.create(
                    result=result_value,
                    period=period_value,
                    student=student,
                    academicsUE=academic_ue,
                    success=is_success,
                    isExempt=request.data.get('isexempt', False)
                )
                
                serializer = ResultSerializer(result)
                
                return ApiResponseClass.created("Résultat créé avec succès", serializer.data)
            except Exception as e:
                return ApiResponseClass.error(f"Erreur lors de la création: {str(e)}",
                                            status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
        try:
            result = get_object_or_404(Result, pk=pk)
            serializer = ResultSerializer(result)
            return ApiResponseClass.success("Résultat récupéré avec succès", serializer.data)
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la récupération du résultat: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    @checkRoleToken([AccountRoleEnum.EDUCATOR, AccountRoleEnum.PROFESSOR])
    def patch(self, request, pk):
        try:
            result = get_object_or_404(Result, pk=pk)
            if request.data.get('approved', False)==True:
                serializer = ResultSerializer(result, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return ApiResponseClass.success("Résultat mis à jour avec succès", serializer.data)
            if hasattr(result, 'approved') and result.approved:
                return ApiResponseClass.error(
                    "Ce résultat a déjà été approuvé et ne peut être modifié",
                    status.HTTP_403_FORBIDDEN
                )

            result_value = request.data.get('result')
           
            period_value = request.data.get('period', result.period)

            # Vérifier que result est dans la plage valide (period * 10)
            max_result = period_value * 10
            min_result = max_result / 2  # 50% pour réussir
            
            if not result.isExempt and result_value is not None:
                if not (min_result <= float(result_value) <= max_result):
                    return ApiResponseClass.error(
                        f"Le résultat doit être entre {min_result} et {max_result} ",
                        status.HTTP_400_BAD_REQUEST
                    )

            # Déterminer si l'étudiant a réussi (success = True si result >= min_result)
            
            if not result.isExempt and result_value is not None:
                is_success = float(result_value) >= min_result
            is_success = True    
            # Mise à jour manuelle du champ success
            request.data['success'] = is_success

            serializer = ResultSerializer(result, data=request.data, partial=True)
            if serializer.is_valid():
                updated_result = serializer.save()
                return ApiResponseClass.success("Résultat mis à jour avec succès", serializer.data)
            return ApiResponseClass.error(serializer.errors, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return ApiResponseClass.error(
                f"Erreur lors de la mise à jour: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AcademicUEGetById(APIView):
    parser_classes = [JSONParser]

    @checkRoleToken([AccountRoleEnum.EDUCATOR,AccountRoleEnum.PROFESSOR])
    @swagger_auto_schema(
        operation_description="Récupère une UE académique par ID avec ses relations",
        responses={
            200: openapi.Response(
                description="UE académique récupérée avec succès",
                schema=AcademicUESerializer()
            ),
            404: openapi.Response(description="UE académique non trouvée")
        }
    )
    def get(self, request, id):
        try:
            academicUE = AcademicUE.objects.select_related('professor').prefetch_related('students','lessons','results').get(id=id)
            serializer = AcademicUESerializer(academicUE)
            return ApiResponseClass.success("Détails de l'UE académique récupérés avec succès", serializer.data)
        except AcademicUE.DoesNotExist:
            return ApiResponseClass.error("UE académique non trouvée", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la récupération de l'UE académique: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

class SectionRegistration(APIView):
    parser_classes = [JSONParser]

    @checkRoleToken([AccountRoleEnum.EDUCATOR])
    @swagger_auto_schema(
        operation_description="Inscrit un étudiant à une section",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['studentId', 'sectionId', 'cycle'],
            properties={
                'studentId': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID de l\'étudiant'),
                'sectionId': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID de la section'),
                'cycle': openapi.Schema(type=openapi.TYPE_INTEGER, description='Cycle d\'études')
            }
        ),
        responses={
            200: openapi.Response(description="Inscription réussie"),
            400: openapi.Response(description="Données invalides"),
            404: openapi.Response(description="Étudiant ou section non trouvé")
        }
    )
    def post(self, request, id=None):
        try:
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
                ues = section.ues.filter(cycle=cycle)
                
                if not ues.exists():
                    return ApiResponseClass.error(
                        f"Aucune UE trouvée pour le cycle {cycle}",
                        status.HTTP_404_NOT_FOUND
                    )

                validation_results = []
                already_registered_ues = []
                available_courses_count = 0

                for ue in ues:
                    academic_ue = ue.academic_ues.filter(year=year).first()
                    
                    if not academic_ue:
                        validation_results.append({
                            'ue_name': ue.name,
                            'has_all_prerequisites': False,
                            'missing_prerequisites': ['UE académique non disponible pour cette année'],
                            'status': 'non_disponible'
                        })
                        continue

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
                    
                    lessons_total = Lesson.objects.filter(academic_ue=academic_ue).count()
                    lessons_completed = Lesson.objects.filter(academic_ue=academic_ue, status=LessonStatus.COMPLETED).count()
                    
                    if lessons_total > 0 and (lessons_completed / lessons_total) >= 0.4:
                        validation_results.append({
                            'ue_name': ue.name,
                            'has_all_prerequisites': False,
                            'missing_prerequisites': ['40% des séances ont déjà été données'],
                            'status': 'trop_tard'
                        })
                        continue

                    if ue.prerequisites.exists():
                        for prerequisite in ue.prerequisites.all():
                            try:
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
                    
                    if has_all_prerequisites:
                        available_courses_count += 1
                    
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

                if available_courses_count == 0:
                    return ApiResponseClass.error(
                        "Aucun cours disponible pour l'inscription. Vérifiez les prérequis et les dates limites.",
                        status.HTTP_400_BAD_REQUEST
                    )

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

class RegisterStudentsToAcademicUE(APIView):
    parser_classes = [JSONParser]
    @checkRoleToken([AccountRoleEnum.EDUCATOR])
    @swagger_auto_schema(
        operation_description="Inscrit plusieurs étudiants à une UE académique",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['student_ids'],
            properties={
                'student_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='Liste des IDs des étudiants à inscrire'
                )
            }
        ),
        responses={
            200: openapi.Response(description="Inscription terminée"),
            400: openapi.Response(description="Données invalides"),
            404: openapi.Response(description="UE académique non trouvée")
        }
    )
    def post(self, request, id):
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

class GetStudentResults(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Récupère les résultats d'un étudiant pour une UE académique",
        responses={
            200: openapi.Response(
                description="Résultats récupérés avec succès",
                schema=ResultSerializer(many=True)
            ),
            404: openapi.Response(description="Aucun résultat trouvé")
        }
    )
   
    def get(self, request, academic_ue, student):
        try:
            results = Result.objects.filter(
                academicsUE_id=academic_ue,
                student_id=student
            )
            
            if not results.exists():
                return ApiResponseClass.success("Aucun résultat trouvé", [])
            serializer = ResultSerializer(results, many=True)
            return ApiResponseClass.success("Résultats récupérés avec succès", serializer.data)

        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la récupération des résultats: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetStudentAcademicUEs(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Récupère toutes les UE académiques d'un étudiant",
        responses={
            200: openapi.Response(
                description="UE académiques récupérées avec succès",
                schema=AcademicUESerializer(many=True)
            ),
            404: openapi.Response(description="Étudiant non trouvé")
        }
    )
    def get(self, request, student_id):
        try:
            student = get_object_or_404(Student, id=student_id)
            academic_ues = AcademicUE.objects.filter(students=student)
            print(academic_ues)
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

class GetEligibleStudentsForAcademicUE(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Récupère tous les étudiants éligibles pour une UE académique",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Terme de recherche pour filtrer les étudiants",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'page',
                openapi.IN_QUERY,
                description="Numéro de page pour la pagination",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'page_size',
                openapi.IN_QUERY,
                description="Nombre d'éléments par page",
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Liste des étudiants éligibles récupérée avec succès",
                schema=StudentAcademicUeRegistrationSerializer(many=True)
            ),
            404: openapi.Response(description="UE académique non trouvée")
        }
    )
    def get(self, request, academicUeId):
        try:
            # Validation de l'ID d'UE académique
            if academicUeId <= 0:
                return ApiResponseClass.error(
                    "L'ID de l'UE académique doit être un nombre positif", 
                    status.HTTP_400_BAD_REQUEST
                )
            
            # Récupération des paramètres de filtrage
            search = request.query_params.get('search', '')
            
            try:
                page = int(request.query_params.get('page', '1'))
                if page < 1:
                    page = 1
            except ValueError:
                page = 1
                
            try:
                page_size = int(request.query_params.get('page_size', '10'))
                page_size = min(max(page_size, 1), 10)  # Limites : minimum 1, maximum 25
            except ValueError:
                page_size = 10

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
            
            # Vérifier s'il y a des résultats
            if total_count == 0:
                return ApiResponseClass.success(
                    "Aucun étudiant éligible trouvé", 
                    {"students": [], "pagination": {"count": 0, "page": page, "page_size": page_size, "total_pages": 0}}
                )
                
            students = query[start_index:end_index]
            
            # Préparation des données des étudiants avec leur statut
            student_data = []
            for student in students:
                
                status = StudentAcademicUeRegistrationStatus.AP.value  # Par défaut, on considère que l'étudiant a tous les prérequis
                lessons=Lesson.objects.all().filter(academic_ue=academic_ue)
                total_lessons_count=lessons.count()
                finished_lessons_count=lessons.filter(status=LessonStatus.COMPLETED).count()
                if(finished_lessons_count/total_lessons_count>=0.4):
                    status=StudentAcademicUeRegistrationStatus.NP.value
               
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
            
            # Préparation des métadonnées de pagination
            
            return ApiResponseClass.success(
                "Liste des étudiants éligibles récupérée avec succès", 
                student_data
            )
        except Student.DoesNotExist:
            return ApiResponseClass.error("Étudiants non trouvés", status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return ApiResponseClass.error(f"Erreur de valeur: {str(e)}", status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return ApiResponseClass.error(
                f"Erreur lors de la récupération des étudiants éligibles: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                {"details": error_details}
            )

class StudentAcademicUeRegistration(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Inscrit un étudiant à une UE académique",
        responses={
            201: openapi.Response(
                description="Inscription réussie",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'student_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'academic_ue_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: openapi.Response(description="L'étudiant n'a pas tous les prérequis nécessaires"),
            404: openapi.Response(description="Étudiant ou UE académique non trouvé"),
            500: openapi.Response(description="Erreur lors de l'inscription")
        }
    )
    def post(self, request, academicUeId, studentId):
        try:
            # Vérification de l'existence de l'UE académique et de l'étudiant
            student = get_object_or_404(Student, id=studentId)
            academic_ue = get_object_or_404(AcademicUE, id=academicUeId)
            
            # Vérification si l'étudiant est déjà inscrit
            if academic_ue.students.filter(id=studentId).exists():
                return ApiResponseClass.error(
                    "L'étudiant est déjà inscrit à cette UE académique",
                    status.HTTP_400_BAD_REQUEST
                )
            
            # Vérification des prérequis
            has_all_prerequisites = True
            missing_prerequisites = []
            
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
                        missing_prerequisites.append(prerequisite.name)

            # Si l'étudiant a tous les prérequis, l'inscrire dans l'UE académique
            if has_all_prerequisites:
                academic_ue.students.add(student)
                return ApiResponseClass.created(
                    "Inscription réussie - L'étudiant a été inscrit à l'UE académique",
                    {
                        "student_id": student.id, 
                        "academic_ue_id": academic_ue.id
                    }
                )
            else:
                return ApiResponseClass.error(
                    f"L'étudiant n'a pas tous les prérequis nécessaires: {', '.join(missing_prerequisites)}",
                    status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return ApiResponseClass.error(
                f"Erreur lors de l'inscription: {str(e)}", 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetStudentAcademicUEDetails(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Récupère les détails d'une UE académique pour un étudiant spécifique",
        responses={
            200: openapi.Response(
                description="Détails de l'UE académique récupérés avec succès",
                schema=AcademicUESerializer()
            ),
            404: openapi.Response(description="UE académique ou étudiant non trouvé")
        }
    )
    def get(self, request, academic_ue_id, student_id):
        try:
            # Récupérer l'UE académique avec toutes ses relations
            academic_ue = AcademicUE.objects.select_related(
                'ue', 'professor'
            ).prefetch_related(
                'lessons', 'results'
            ).get(id=academic_ue_id)

            # Vérifier si l'étudiant est inscrit à cette UE
            if not academic_ue.students.filter(id=student_id).exists():
                return ApiResponseClass.error(
                    "L'étudiant n'est pas inscrit à cette UE académique",
                    status.HTTP_404_NOT_FOUND
                )

            # Récupérer les présences pour les leçons de cette UE
            attendances = Attendance.objects.filter(
                lesson__academic_ue=academic_ue,
                student_id=student_id
            ).select_related('lesson')

            # Créer un dictionnaire avec les données de l'UE académique
            data = {
                'id': academic_ue.id,
                'year': academic_ue.year,
                'start_date': academic_ue.start_date,
                'end_date': academic_ue.end_date,
                'ue': academic_ue.ue,
                'professor': academic_ue.professor,
                'students': academic_ue.students.filter(id=student_id),
                'lessons': academic_ue.lessons.all(),
                'results': academic_ue.results.filter(student_id=student_id),
            }

            # Sérialiser les données
            serializer = AcademicUEDetailsSerializer(data)
            serializer.data.attendances = Attendance.objects.all().filter(lesson__academic_ue=academic_ue, student_id=student_id)
            return ApiResponseClass.success(
                "Détails de l'UE académique récupérés avec succès",
                serializer.data
            )
        except AcademicUE.DoesNotExist:
            return ApiResponseClass.error(
                "UE académique non trouvée",
                status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return ApiResponseClass.error(
                f"Erreur lors de la récupération des détails de l'UE académique: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
