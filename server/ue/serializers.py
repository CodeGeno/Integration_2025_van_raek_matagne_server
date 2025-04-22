from rest_framework import serializers
from .models import UE





class UESerializer(serializers.ModelSerializer):
    def get_prerequisites(self, obj):
        # Récupérer les prérequis associés et les sérialiser
        prerequisites = obj.prerequisites.all()
        return UESerializer(prerequisites, many=True).data 
    prerequisites = serializers.SerializerMethodField("get_prerequisites")
    class Meta:
        model = UE
        fields = ['ueId', 'name', 'description', 'isActive', 'section', 'prerequisites','cycle','periods']

    