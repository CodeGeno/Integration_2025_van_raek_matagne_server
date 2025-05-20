from django.db import models

from security.models import Student
from ue_management.models import Lesson
from enum import Enum

class AttendanceStatusEnum(Enum):
    P = "Présentiel"
    M = "Distanciel"
    CM = "Certificat médical"
    A = "Absence non justifiée"
    ABANDON = "Abandon"
    D = "Dispensé"


class Attendance(models.Model):
    lesson= models.ForeignKey(Lesson, on_delete=models.CASCADE)
    student= models.ForeignKey(Student, on_delete=models.CASCADE)
    status= models.CharField(max_length=255, choices=[(status.value, status.name) for status in AttendanceStatusEnum])

