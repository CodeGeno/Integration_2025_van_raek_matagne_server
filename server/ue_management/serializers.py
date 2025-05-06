from rest_framework import serializers

from ue_management.models import Lesson, AcademicUE, Result
from attendance.models import Attendance
from attendance.serializer import AttendanceSerializer

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
    ue = serializers.SerializerMethodField()

    class Meta:
        model = AcademicUE
        fields = '__all__'

    def get_ue(self, obj):
        if hasattr(obj, 'ue') and obj.ue:
            from ue.serializers import UESerializer
            return UESerializer(obj.ue).data
        return None