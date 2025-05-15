from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Attendance
from .serializers import AttendanceSerializer, AttendanceUpsertSerializer
from security.decorators import checkRoleToken, jwt_required
from security.models import AccountRoleEnum
from api.models import ApiResponseClass
from django.db import transaction
from django.shortcuts import get_object_or_404
from ue_management.models import AcademicUE, Lesson, LessonStatus
from security.models import Student
from attendance.models import AttendanceStatusEnum
from security.serializers import StudentSerializer, EmployeeSerializer
from ue_management.serializers import AcademicUESerializer, LessonDetailSerializer
from ue.serializers import UESerializer

class AttendanceListByLessonIdView(APIView):
    @checkRoleToken([AccountRoleEnum.PROFESSOR, AccountRoleEnum.EDUCATOR])
    def get(self, request, lessonId):
        lesson = get_object_or_404(Lesson, id=lessonId)
        attendances = Attendance.objects.filter(lesson=lesson)
       
        studentsData = StudentSerializer(lesson.academic_ue.students.all(), many=True)
        academicUeData = AcademicUESerializer(lesson.academic_ue)
        ueData = UESerializer(lesson.academic_ue.ue)
        professorData = EmployeeSerializer(lesson.academic_ue.professor)
        attendanceData = AttendanceSerializer(attendances, many=True)
        lessonData = LessonDetailSerializer(lesson)
        
        # Combiner les données
        response_data = {
            "professor": professorData.data,
            "attendances": attendanceData.data,
            "students": studentsData.data,
            "academicUe": academicUeData.data,
            "ue": ueData.data,
            "lesson": lessonData.data
        }
        
        return ApiResponseClass.success("Détails de la leçon et présences récupérés avec succès", response_data)


class AttendanceUpsertView(APIView):
    @checkRoleToken([AccountRoleEnum.PROFESSOR, AccountRoleEnum.EDUCATOR])
    def post(self, request):
        # Vérifier si les données envoyées sont une liste
        if isinstance(request.data, list):
            # Utiliser une transaction pour garantir l'atomicité
            with transaction.atomic():
                # Valider d'abord toutes les données avant de sauvegarder
                serializers = []
                all_valid = True
                validation_errors = []
                lesson_ids = set()  # Pour stocker les IDs des leçons concernées
                
                for index, attendance_data in enumerate(request.data):
                    print(f"Traitement des données pour l'index {index}:", attendance_data)
                    # Vérifier l'existence de la leçon et de l'étudiant
                    try:
                        lesson = Lesson.objects.get(id=attendance_data.get('lesson_id'))
                        student = Student.objects.get(id=attendance_data.get('student_id'))
                        lesson_ids.add(lesson.id)  # Ajouter l'ID de la leçon
                    except (Lesson.DoesNotExist, Student.DoesNotExist) as e:
                        all_valid = False
                        validation_errors.append({
                            "index": index,
                            "errors": f"Leçon ou étudiant non trouvé: {str(e)}"
                        })
                        continue

                    # Vérifier si la présence existe déjà
                    try:
                        existing_attendance = Attendance.objects.get(
                            lesson=lesson,
                            student=student
                        )
                        serializer = AttendanceUpsertSerializer(existing_attendance, data=attendance_data, partial=True)
                    except Attendance.DoesNotExist:
                        serializer = AttendanceUpsertSerializer(data=attendance_data)

                    if serializer.is_valid():
                        serializers.append(serializer)
                    else:
                        print(f"Erreurs de validation pour l'index {index}:", serializer.errors)
                        all_valid = False
                        validation_errors.append({
                            "index": index,
                            "errors": serializer.errors
                        })
                
                # Si toutes les données sont valides, sauvegarder
                if all_valid:
                    created_attendances = [serializer.save() for serializer in serializers]
                    response_data = [AttendanceSerializer(attendance).data for attendance in created_attendances]
                    
                    # Mettre à jour le statut des leçons
                    for lesson_id in lesson_ids:
                        lesson = Lesson.objects.get(id=lesson_id)
                        lesson.status = LessonStatus.COMPLETED
                        lesson.save()
                    
                    return ApiResponseClass.created("Toutes les présences ont été créées/mises à jour avec succès", response_data)
                else:
                    # Si une seule entrée est invalide, annuler la transaction et retourner les erreurs
                    transaction.set_rollback(True)
                    return ApiResponseClass.error({
                        "message": "La création/mise à jour des présences a échoué. Aucune présence n'a été modifiée.",
                        "errors": validation_errors
                    })
        else:
            # Traiter une seule présence si les données ne sont pas une liste
            print("Données reçues:", request.data)
            try:
                lesson = Lesson.objects.get(id=request.data.get('lesson_id'))
                student = Student.objects.get(id=request.data.get('student_id'))
            except (Lesson.DoesNotExist, Student.DoesNotExist) as e:
                return ApiResponseClass.error(f"Leçon ou étudiant non trouvé: {str(e)}")
            try:
                existing_attendance = Attendance.objects.get(
                    lesson=lesson,
                    student=student
                )
                serializer = AttendanceUpsertSerializer(existing_attendance, data=request.data, partial=True)
            except Attendance.DoesNotExist:
                serializer = AttendanceUpsertSerializer(data=request.data)

            if serializer.is_valid():
                attendance = serializer.save()
                # Mettre à jour le statut de la leçon
                lesson.status = LessonStatus.COMPLETED
                lesson.save()
                return ApiResponseClass.created("Présence créée/mise à jour avec succès", serializer.data)
            print("Erreurs de validation:", serializer.errors)
            return ApiResponseClass.error(serializer.errors)
    
class AttendanceValidationView(APIView):
    @checkRoleToken([AccountRoleEnum.PROFESSOR, AccountRoleEnum.EDUCATOR])
    def post(self, request):
        # Vérifier si les données envoyées sont une liste
        if isinstance(request.data, list):
            # Utiliser une transaction pour garantir l'atomicité
            with transaction.atomic():
                # Valider d'abord toutes les données avant de sauvegarder
                serializers = []
                all_valid = True
                validation_errors = []
                
                for index, attendance_data in enumerate(request.data):
                    serializer = AttendanceUpsertSerializer(data=attendance_data)
                    if serializer.is_valid():
                        serializers.append(serializer)
                    else:
                        all_valid = False
                        validation_errors.append({
                            "index": index,
                            "errors": serializer.errors
                        })
                
                # Si toutes les données sont valides, sauvegarder
                if all_valid:
                    validated_attendances = [serializer.save() for serializer in serializers]
                    response_data = [AttendanceSerializer(attendance).data for attendance in validated_attendances]
                    return ApiResponseClass.created("Toutes les présences ont été validées avec succès", response_data)
                else:
                    # Si une seule entrée est invalide, annuler la transaction et retourner les erreurs
                    transaction.set_rollback(True)
                    return ApiResponseClass.error({
                        "success": False,
                        "message": "La validation des présences a échoué. Aucune présence n'a été validée.",
                        "errors": validation_errors
                    }, status=status.HTTP_400_BAD_REQUEST)  
        else:
            # Traiter une seule présence si les données ne sont pas une liste
            serializer = AttendanceSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return ApiResponseClass.created("Présence validée avec succès", serializer.data)
            return ApiResponseClass.error(serializer.errors)


class StudentAcademicUeDropoutView(APIView):
    @checkRoleToken([AccountRoleEnum.EDUCATOR])
    def post(self, request, academicUeId, studentId):
        try:
            # Vérification de l'existence de l'UE académique et de l'étudiant
            student = get_object_or_404(Student, id=studentId)
            academic_ue = get_object_or_404(AcademicUE, id=academicUeId)
            if academic_ue.students.filter(id=studentId).exists():
                lessons = Lesson.objects.filter(academic_ue=academic_ue)
                for lesson in lessons:
                    attendance, created = Attendance.objects.get_or_create(
                        lesson=lesson,
                        student=student,
                        defaults={'status': AttendanceStatusEnum.ABANDON.value}
                    )
                    if not created:
                        # Mettre à jour le statut de présence existant
                        attendance.status = AttendanceStatusEnum.ABANDON.value
                        attendance.save()
                
                # Mettre à jour le statut de l'étudiant dans l'UE
                academic_ue.students.remove(student)
                
                return ApiResponseClass.success(
                    f"L'étudiant {student.contactDetails.firstName} {student.contactDetails.lastName} a été marqué comme abandonné pour l'UE {academic_ue.ue.name}",
                    {
                        "student_id": studentId,
                        "academic_ue_id": academicUeId,
                        "status": "ABANDON"
                    }
                )
            else:
                return ApiResponseClass.error(
                    f"L'étudiant {student.contactDetails.firstName} {student.contactDetails.lastName} n'est pas inscrit à l'UE {academic_ue.ue.name}",
                    status.HTTP_404_NOT_FOUND
                )
        except Student.DoesNotExist:
            return ApiResponseClass.error(f"Étudiant avec l'ID {studentId} non trouvé", status.HTTP_404_NOT_FOUND)
        except AcademicUE.DoesNotExist:
            return ApiResponseClass.error(f"UE académique avec l'ID {academicUeId} non trouvée", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return ApiResponseClass.error(f"Une erreur s'est produite: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)