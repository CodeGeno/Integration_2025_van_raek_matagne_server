import serializers

from server.ue_management.models import Lesson, AcademicUE, Result


class AcademicUESerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicUE
        fields = '__all__'

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'