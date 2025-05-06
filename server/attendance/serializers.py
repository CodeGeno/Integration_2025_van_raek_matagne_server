from rest_framework import serializers
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__' 

class AttendanceValidationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__' 