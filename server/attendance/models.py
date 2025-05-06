from django.db import models

from security.models import Student
from ue_management.models import Lesson
from enum import Enum
# Create your models here.

class AttendanceStatusEnum(Enum):
    PRESENT = 'P'
    PRESENT_DISTANCIEL = 'M'
    ABSENT_NON_JUSTIFIE = 'A'
    ABSENT_SOUS_CERTIFICAT = 'CM'
    DISPENSE = 'D'
    ABANDON = 'Abandon'


class Attendance(models.Model):
    lesson= models.ForeignKey(Lesson, on_delete=models.CASCADE)
    student= models.ForeignKey(Student, on_delete=models.CASCADE)
    status= models.CharField(max_length=255, choices=[(status.value, status.name) for status in AttendanceStatusEnum])

