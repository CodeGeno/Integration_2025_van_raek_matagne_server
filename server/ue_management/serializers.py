import serializers

from server.ue_management.models import Lesson, AcademicUE, Result


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'


class AcademicUESerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    results = ResultSerializer(many=True, read_only=True)

    class Meta:
        model = AcademicUE
        fields = '__all__'