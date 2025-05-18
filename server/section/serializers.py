from rest_framework import serializers
from .models import Section, SectionType, SectionCategory, SECTION_TYPE_CHOICES, SECTION_CATEGORY_CHOICES
from ue.serializers import UESerializer

# Créer des dictionnaires pour convertir facilement entre nom et valeur
TYPE_NAME_TO_VALUE = {type_enum.name: type_enum.value for type_enum in SectionType}
TYPE_VALUE_TO_NAME = {type_enum.value: type_enum.name for type_enum in SectionType}
CATEGORY_NAME_TO_VALUE = {cat_enum.name: cat_enum.value for cat_enum in SectionCategory}
CATEGORY_VALUE_TO_NAME = {cat_enum.value: cat_enum.name for cat_enum in SectionCategory}

class SectionTypeField(serializers.Field):
    def to_representation(self, value):
        # Lors de la sérialisation, convertir le nom (MASTER) en valeur (Master) pour l'affichage
        return TYPE_NAME_TO_VALUE.get(value, value)

    def to_internal_value(self, data):
        # Lors de la désérialisation, conserver le nom d'énumération si c'est un nom valide
        if data in TYPE_NAME_TO_VALUE:
            return data
        # Sinon, essayer de trouver le nom correspondant à la valeur
        for type_enum in SectionType:
            if type_enum.value == data:
                return type_enum.name
        raise serializers.ValidationError(f"'{data}' n'est pas un type de section valide. Options: {[t.name for t in SectionType]}")

class SectionCategoryField(serializers.Field):
    def to_representation(self, value):
        # Lors de la sérialisation, convertir le nom (SOCIAL) en valeur (Sociale) pour l'affichage
        return CATEGORY_NAME_TO_VALUE.get(value, value)

    def to_internal_value(self, data):
        # Lors de la désérialisation, conserver le nom d'énumération si c'est un nom valide
        if data in CATEGORY_NAME_TO_VALUE:
            return data
        # Sinon, essayer de trouver le nom correspondant à la valeur
        for cat_enum in SectionCategory:
            if cat_enum.value == data:
                return cat_enum.name
        raise serializers.ValidationError(f"'{data}' n'est pas une catégorie de section valide. Options: {[c.name for c in SectionCategory]}")

class SectionSerializer(serializers.ModelSerializer):
    sectionType = SectionTypeField()
    sectionCategory = SectionCategoryField()
    ues = UESerializer(many=True, read_only=True)
    
    class Meta:
        model = Section
        fields = '__all__'
        read_only_fields = ('id', 'ues')

    def to_representation(self, instance):
        # Personnaliser la représentation pour convertir les noms d'énumération en valeurs pour l'affichage
        ret = super().to_representation(instance)
        
        # Les conversions sont maintenant gérées par les champs personnalisés
        return ret
    
    def to_internal_value(self, data):
        # Cette méthode est appelée avant la validation
        # Inclure les données brutes pour débogage
        return super().to_internal_value(data)

class SectionCreationSerializer(serializers.ModelSerializer):
    sectionType = SectionTypeField()
    sectionCategory = SectionCategoryField()
    
    class Meta:
        model = Section
        fields = '__all__'
        
    def to_internal_value(self, data):
        # Même logique que SectionSerializer pour la conversion des énumérations
        if 'sectionType' in data:
            for type_enum in SectionType:
                if type_enum.name == data['sectionType']:
                    data = data.copy()
                    data['sectionType'] = type_enum.value
                    break
        
        if 'sectionCategory' in data:
            for cat_enum in SectionCategory:
                if cat_enum.name == data['sectionCategory']:
                    data = data.copy() if 'sectionType' not in data else data
                    data['sectionCategory'] = cat_enum.value
                    break
        
        return super().to_internal_value(data)
        