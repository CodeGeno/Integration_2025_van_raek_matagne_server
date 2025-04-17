# server/ue_management/views.py
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from server.security.decorators import has_employee_role
from server.security.entities.accountTypeEnum import EmployeRoleEnum
from server.ue_management.models import Lesson, AcademicUE, Result
from server.ue_management.serializers import LessonSerializer, AcademicUESerializer, ResultSerializer


class AcademicUEView(APIView):
    def get(self, request):
        academic_ues = AcademicUE.objects.all()
        serializer = AcademicUESerializer(academic_ues, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # @has_employee_role(EmployeRoleEnum.ADMINISTRATOR)
        serializer = AcademicUESerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        # @has_employee_role(EmployeRoleEnum.ADMINISTRATOR)
        academic_ue = get_object_or_404(AcademicUE, pk=pk)
        serializer = AcademicUESerializer(academic_ue, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LessonView(APIView):
    def get(self, request):
        lessons = Lesson.objects.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # @has_employee_role(EmployeRoleEnum.ADMINISTRATOR)
        serializer = LessonSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        # @has_employee_role(EmployeRoleEnum.ADMINISTRATOR)
        lesson = get_object_or_404(Lesson, pk=pk)
        serializer = LessonSerializer(lesson, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResultView(APIView):
    def get(self, request):
        results = Result.objects.all()
        serializer = ResultSerializer(results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # @has_employee_role(EmployeRoleEnum.ADMINISTRATOR)
        serializer = ResultSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        # @has_employee_role(EmployeRoleEnum.ADMINISTRATOR)
        result = get_object_or_404(Result, pk=pk)
        serializer = ResultSerializer(result, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)