from django.db import models

from ue.models import UE

class AcademicUE(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    ue = models.ForeignKey(UE, on_delete=models.CASCADE, related_name='academic_ues')

    def __str__(self):
        return f"{self.ue.libelle} - {self.year}"

class Lesson(models.Model):
    id = models.AutoField(primary_key=True)
    academic_ue = models.ForeignKey(AcademicUE, on_delete=models.CASCADE, related_name='lessons')
    lesson_date = models.DateField()

    def __str__(self):
        return f"Séance du {self.lesson_date} - {self.academic_ue}"

class Result(models.Model):
    academic_ue = models.ForeignKey(AcademicUE, on_delete=models.CASCADE, related_name='results')
    #add foreign key to student
    result = models.IntegerField(null=True, blank=True)
    period = models.IntegerField()
    success = models.BooleanField(default=False)
    is_exempt = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student} - {self.academic_ue}"

    # class Meta:
    #     unique_together = ('academic_ue', 'student')