from django.db import models
from section.models import Lesson
from security.models import Student

# Create your models here.

class Attendance(models.Model):
    lesson= models.ForeignKey(Lesson, on_delete=models.CASCADE)
    student= models.ForeignKey(Student, on_delete=models.CASCADE)

