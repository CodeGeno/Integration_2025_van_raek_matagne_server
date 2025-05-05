from rest_framework import serializers
from .models import Section,SectionType,SectionCategory

class SectionSerializer(serializers.ModelSerializer):
    sectionType = serializers.SerializerMethodField()
    sectionCategory = serializers.SerializerMethodField()
    def get_sectionType(self, obj):
           print(obj.sectionType)
           # Trouver l'énumération correspondant à la valeur stockée
           for type_enum in SectionType:
               if type_enum.name == obj.sectionType:
                   return type_enum.value
           return obj.sectionType
    def get_sectionCategory(self, obj):
           print(obj.sectionCategory)
           # Trouver l'énumération correspondant à la valeur stockée
           for category_enum in SectionCategory:
               if category_enum.name == obj.sectionCategory:
                   return category_enum.value
           return obj.sectionCategory
    class Meta:
        model = Section
        fields = '__all__'

class SectionCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'
        