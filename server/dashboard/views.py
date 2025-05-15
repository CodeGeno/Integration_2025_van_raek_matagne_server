# server/dashboard/views.py
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.models import ApiResponseClass
from security.decorators import jwt_required
from security.entities.accountTypeEnum import AccountRoleEnum
from ue_management.models import AcademicUE, StudentAcademicUeRegistrationStatus, Result
from ue_management.serializers import AcademicUESerializer
from django.db.models import Q
from datetime import datetime

class StudentDashboardView(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Récupère les cours et résultats d'un étudiant pour le dashboard",
        responses={
            200: openapi.Response(
                description="Données du dashboard récupérées avec succès",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'courses': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                                    'status': openapi.Schema(type=openapi.TYPE_STRING),
                                    'result': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True)
                                }
                            )
                        )
                    }
                )
            ),
            404: openapi.Response(description="Étudiant non trouvé")
        }
    )
    @jwt_required
    def get(self, request):
        try:
            # Récupérer l'ID de l'étudiant depuis le token JWT
            student_id = request.user.id
            current_year = datetime.now().year

            # Récupérer toutes les inscriptions de l'étudiant pour l'année en cours
            registrations = StudentAcademicUeRegistrationStatus.objects.filter(
                student_id=student_id,
                academic_ue__year=current_year
            ).select_related('academic_ue', 'academic_ue__ue')

            courses_data = []
            for reg in registrations:
                course_data = {
                    'id': reg.academic_ue.id,
                    'name': reg.academic_ue.ue.name,
                    'status': reg.status,
                }

                # Vérifier s'il y a un résultat pour ce cours
                result = Result.objects.filter(
                    student_id=student_id,
                    academic_ue=reg.academic_ue
                ).first()

                if result:
                    course_data['result'] = result.result

                courses_data.append(course_data)

            return ApiResponseClass.success(
                "Données du dashboard récupérées avec succès",
                {'courses': courses_data}
            )

        except Exception as e:
            return ApiResponseClass.error(
                f"Erreur lors de la récupération des données du dashboard: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TeacherDashboardView(APIView):
    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_description="Récupère les UE académiques enseignées par un professeur",
        responses={
            200: openapi.Response(
                description="UE académiques récupérées avec succès",
                schema=AcademicUESerializer(many=True)
            )
        }
    )
    @jwt_required
    def get(self, request):
        try:
            # Récupérer l'ID du professeur depuis le token JWT
            teacher_id = request.user.id
            current_year = datetime.now().year

            # Récupérer toutes les UE académiques du professeur pour l'année en cours
            academic_ues = AcademicUE.objects.filter(
                teacher_id=teacher_id,
                year=current_year
            ).select_related('ue')

            serializer = AcademicUESerializer(academic_ues, many=True)
            return ApiResponseClass.success(
                "UE académiques récupérées avec succès",
                serializer.data
            )

        except Exception as e:
            return ApiResponseClass.error(
                f"Erreur lors de la récupération des UE académiques: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 