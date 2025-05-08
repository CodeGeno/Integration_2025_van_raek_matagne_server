from rest_framework import serializers

from ue_management.models import Lesson, AcademicUE, Result
from attendance.models import Attendance
from attendance.serializer import AttendanceSerializer
from ue.models import UE
from security.models import Employee
from security.entities.accountTypeEnum import AccountRoleEnum
from security.serializers import StudentSerializer, EmployeeSerializer
from ue.serializers import UESerializer

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
    ue = UESerializer(read_only=True)
    professor = EmployeeSerializer(read_only=True)
    class Meta:
        model = AcademicUE
        fields = '__all__'

   