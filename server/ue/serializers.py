from rest_framework import serializers
from .models import UE

class UESerializer(serializers.ModelSerializer):
    class Meta:
        model = UE
        fields = '__all__' 