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

class Section(models.Model):
    sectionId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False)
    sectionType = models.CharField(max_length=255, blank=False, choices=[(type.value, type.name) for type in SectionType])
    sectionCategory = models.CharField(max_length=255, blank=False, choices=[(cat.value, cat.name) for cat in SectionCategory])
    description = models.TextField(blank=True)
    isActive = models.BooleanField(default=True)

