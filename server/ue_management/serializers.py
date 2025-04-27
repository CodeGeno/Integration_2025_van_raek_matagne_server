from rest_framework import serializers

from ue_management.models import Lesson, AcademicUE, Result, Attendance

from security.serializers import StudentSerializer


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class ResultSerializer(serializers.ModelSerializer):
    academicsueId = serializers.IntegerField(source='academicsUE_id', write_only=True)
    studentid = serializers.IntegerField(source='student_id', write_only=True)

    class Meta:
        model = Result
        fields = ['academicsueId', 'result', 'period', 'studentid', 'success', 'isExempt']

class AcademicUESerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    results = ResultSerializer(many=True, read_only=True)
    students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = AcademicUE
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'