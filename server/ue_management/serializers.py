from rest_framework import serializers

from ue_management.models import Lesson, AcademicUE, Result, StudentAcademicUeRegistrationStatus
from attendance.models import Attendance
from attendance.serializers import AttendanceSerializer
from ue.models import UE
from security.models import Employee
from security.entities.accountTypeEnum import AccountRoleEnum
from security.serializers import StudentSerializer, EmployeeSerializer
from ue.serializers import UESerializer
from .models import StudentAcademicUeRegistration

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'lesson_date', 'status']


class ResultSerializer(serializers.ModelSerializer):
    academicsueId = serializers.IntegerField(source='academicsUE_id', write_only=True)
    studentid = serializers.IntegerField(source='student_id', write_only=True)

    class Meta:
        model = Result
        fields = ['id', 'academicsueId', 'result', 'period', 'studentid', 'success', 'isExempt', 'approved']

class AcademicUESerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    results = ResultSerializer(many=True, read_only=True)
    students = StudentSerializer(many=True, read_only=True)
    ue = UESerializer(read_only=True)
    professor = EmployeeSerializer(read_only=True)
    lessons_data = LessonSerializer(many=True, write_only=True, required=False)
    ue_id = serializers.IntegerField(write_only=True)
    professor_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = AcademicUE
        fields = ['id', 'year', 'start_date', 'end_date', 'ue', 'students', 'professor', 
                 'lessons', 'results', 'lessons_data', 'ue_id', 'professor_id']

    def create(self, validated_data):
        lessons_data = validated_data.pop('lessons_data', [])
        ue_id = validated_data.pop('ue_id')
        professor_id = validated_data.pop('professor_id', None)
        
        try:
            ue = UE.objects.get(id=ue_id)
        except UE.DoesNotExist:
            raise serializers.ValidationError(f"UE with id {ue_id} does not exist")

        professor = None
        if professor_id:
            try:
                professor = Employee.objects.get(id=professor_id)
            except Employee.DoesNotExist:
                raise serializers.ValidationError(f"Professor with id {professor_id} does not exist")
            
        academic_ue = AcademicUE.objects.create(
            ue=ue,
            professor=professor,
            year=validated_data['year'],
            start_date=validated_data['start_date'],
            end_date=validated_data['end_date']
        )
        
        for lesson_data in lessons_data:
            Lesson.objects.create(
                academic_ue=academic_ue,
                lesson_date=lesson_data['lesson_date']
            )
            
        return academic_ue

class StudentRegistrationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAcademicUeRegistration      
        fields = ['id', 'academicUeId', 'studentId', 'status']

class StudentAcademicUeRegistrationSerializer(StudentSerializer):
    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return getattr(obj, 'status', StudentAcademicUeRegistrationStatus.AP.value)

    class Meta:
        model = StudentAcademicUeRegistration
        fields = ['id', 'email', 'identifier', 'contactDetails', 'status']

class LessonDetailSerializer(serializers.ModelSerializer):
    academic_ue = AcademicUESerializer(read_only=True)
    students = StudentSerializer(many=True, read_only=True)

   

    class Meta:
        model = Lesson
        fields = ['id', 'lesson_date', 'status', 'academic_ue', 'students']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Récupérer l'UE académique et les étudiants
        academic_ue = instance.academic_ue
        students = academic_ue.students.all()
        
        # Ajouter les données de l'UE académique
        data['academic_ue'] = AcademicUESerializer(academic_ue).data
        
        # Ajouter les données des étudiants
        data['students'] = StudentSerializer(students, many=True).data
        
        return data