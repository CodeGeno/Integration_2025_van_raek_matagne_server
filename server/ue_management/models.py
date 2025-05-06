from django.db import models

from ue.models import UE

from security.models import Student, Employee

class AcademicUE(models.Model):
    id = models.AutoField(primary_key=True)
    year = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    ue = models.ForeignKey(UE, on_delete=models.CASCADE, related_name='academic_ues')
    students = models.ManyToManyField(Student, related_name='enrolled_ues')
    professor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='taught_ues')

    def __str__(self):
        return f"{self.ue.name} - {self.year}"

    class Meta:
        unique_together = ('year', 'ue')

class Lesson(models.Model):
    id = models.AutoField(primary_key=True)
    academic_ue = models.ForeignKey(AcademicUE, on_delete=models.CASCADE, related_name='lessons')
    lesson_date = models.DateField()

    def __str__(self):
        return f"Séance du {self.lesson_date} - {self.academic_ue}"


class Result(models.Model):
    id = models.AutoField(primary_key=True)
    academicsUE = models.ForeignKey(AcademicUE, on_delete=models.CASCADE, related_name='results')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    result = models.IntegerField(null=True, blank=True)
    period = models.IntegerField()
    success = models.BooleanField(default=False)
    isExempt = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('academicsUE', 'student')


