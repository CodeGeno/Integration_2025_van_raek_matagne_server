from django.db import models
from section.models import Section


# Create your models here.
class UE(models.Model):
    ueId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='ues')  # Relation un à plusieurs
    prerequisites = models.ManyToManyField('self', symmetrical=False, related_name='required_for')
    isActive = models.BooleanField(default=True)
    cycle=models.IntegerField(blank=False)
    periods=models.IntegerField(blank=False)