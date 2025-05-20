from django.db import models
from enum import Enum



class SectionType(Enum):
    MASTER = "Master"
    BACHELOR = "Bachelier"

class SectionCategory(Enum):
    ECONOMIC = "Économique"
    PARAMEDICAL = "Paramédicale"
    PEDAGOGICAL = "Pédagogique"
    SOCIAL = "Sociale"
    TECHNICAL = "Technique"
    AGRONOMIC = "Agronomique"
    ARTISTIC = "Artistique"

# Utiliser les noms d'énumération (clés) comme valeurs stockées en DB
SECTION_TYPE_CHOICES = [(type_enum.name, type_enum.value) for type_enum in SectionType]
SECTION_CATEGORY_CHOICES = [(cat_enum.name, cat_enum.value) for cat_enum in SectionCategory]

class Section(models.Model):
    name = models.CharField(max_length=255, blank=False)
    sectionType = models.CharField(max_length=255, blank=False, choices=SECTION_TYPE_CHOICES)
    sectionCategory = models.CharField(max_length=255, blank=False, choices=SECTION_CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    isActive = models.BooleanField(default=True)

