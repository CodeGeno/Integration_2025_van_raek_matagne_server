# server/ue_management/views.py
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from security.entities.accountTypeEnum import AccountRoleEnum
from ue_management.models import Lesson, AcademicUE, Result
from ue_management.serializers import LessonSerializer, AcademicUESerializer, ResultSerializer

from api.models import ApiResponseClass


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
        serializer = AcademicUESerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return ApiResponseClass.created("UE académique créée avec succès", serializer.data)
        return ApiResponseClass.error(serializer.errors, status.HTTP_400_BAD_REQUEST)


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
        @has_employee_role([AccountRoleEnum.ADMINISTRATOR])
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
                return ApiResponseClass.error(f"Erreur lor      s de la mise à jour: {str(e)}",
                                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return update_result(request, pk)