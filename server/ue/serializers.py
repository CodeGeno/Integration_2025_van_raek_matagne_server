from rest_framework import serializers
from .models import UE





class UESerializer(serializers.ModelSerializer):
    prerequisites = serializers.SerializerMethodField()

    def get_prerequisites(self, obj):
        # Récupérer les prérequis associés
        prerequisites = obj.prerequisites.all()
        # Retourner un tableau d'objets avec id et name
        return [{'id': prereq.id, 'name': prereq.name} for prereq in prerequisites]

    class Meta:
        model = UE
        fields = '__all__'

    