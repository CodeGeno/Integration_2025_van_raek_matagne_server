from rest_framework import serializers
from .models import Attendance, AttendanceStatusEnum

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__' 

class AttendanceValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__' 

class AttendanceUpsertSerializer(serializers.ModelSerializer):
    lesson_id = serializers.IntegerField(write_only=True)
    student_id = serializers.IntegerField(write_only=True)
    status = serializers.ChoiceField(choices=[
        ('P', 'Présentiel'),
        ('M', 'Distanciel'),
        ('CM', 'Certificat médical'),
        ('A', 'Absence non justifiée'),
        ('ABANDON', 'Abandon'),
        ('D', 'Dispensé')
    ])

    class Meta:
        model = Attendance
        fields = ['id', 'lesson_id', 'student_id', 'status', 'lesson', 'student']
        read_only_fields = ['id', 'lesson', 'student']
    
    def create(self, validated_data):
        lesson_id = validated_data.pop('lesson_id')
        student_id = validated_data.pop('student_id')
        return Attendance.objects.create(
            lesson_id=lesson_id,
            student_id=student_id,
            **validated_data
        )

    def update(self, instance, validated_data):
        if 'lesson_id' in validated_data:
            instance.lesson_id = validated_data.pop('lesson_id')
        if 'student_id' in validated_data:
            instance.student_id = validated_data.pop('student_id')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
