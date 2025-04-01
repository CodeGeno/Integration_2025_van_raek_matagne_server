# api/security/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .decorators import jwt_required
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Student, ContactDetails, Address, Educator,Administrators
from .decorators import has_employee_role
from .entities.accountTypeEnum import EmployeRoleEnum
import jwt
from django.conf import settings
from .models import Account
SECRET_KEY = "264acbe227697c2106fec96de2608ffa9696eea8d4bec4234a4d49e099decc7448daafbc7ba2f4d7b127460936a200f9885c220e81c929525e310084a7abea6fc523f0b2a2241bc91899f158f4c437b059141ffc24642dfa2254842ae8acab96460e05a6293aea8a31f44aa860470b8d972d5f4d1adec181bf79d77fe4a2eed0eed7189da484c5601591ca222b11ff0ca56fce663f838cd4f1a5cddcec78f3821ac0da9769b848147238928f24d59849c7bb8dbf12697d214f04d7fbd476f38c3b360895b1e09d9c0d1291fd61452efb0616034baf32492550b3067d0a3adf317a6808da8555f1cffca990c0452e97d48c8becb77ccdda4290146c49b1c5a8b5"


class StudentCreationEndpoint(APIView):
    @has_employee_role(EmployeRoleEnum.ADMINISTRATOR, EmployeRoleEnum.EDUCATOR)
    def post(self, request, *args, **kwargs):
        try:
            # Créer d'abord les détails de contact
            contact_details_data = request.data.get('contact_details')
            contact_details = ContactDetails.objects.create(**contact_details_data)

            # Créer l'adresse
            address_data = request.data.get('address')
            address = Address.objects.create(**address_data)

            # Créer l'étudiant
            student = Student.objects.create(
                password=request.data['password'],
                contact_details=contact_details,
                address=address
            )
            
            return Response({
                "message": "Compte étudiant créé avec succès",
                "student_email": student.studentEmail
            }, status=status.HTTP_201_CREATED)

        except KeyError as e:
            return Response({
                "error": f"Champ requis manquant: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "error": f"Erreur lors de la création: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class EmployeeCreationEndpoint(APIView):
   
    def post(self, request, *args, **kwargs):
        try:
            # Créer d'abord les détails de contact
            contact_details_data = request.data.get('contact_details')
            contact_details = ContactDetails.objects.create(**contact_details_data)

            # Créer l'adresse
            address_data = request.data.get('address')
            address = Address.objects.create(**address_data)

            match request.data.get('employee_role'):
                case EmployeRoleEnum.ADMINISTRATOR.name:    
                    employee = Administrator.objects.create(
                        password=request.data['password'],
                        contact_details=contact_details,
                        address=address
                    )
                case EmployeRoleEnum.EDUCATOR.name:
                    employee = Educator.objects.create(
                        password=request.data['password'],
                        contact_details=contact_details,
                        address=address
                    )
            
            return Response({
                "message": "Compte employé créé avec succès",
                "employee_email": employee.employeeEmail,
                "employee_matricule": employee.matricule
            }, status=status.HTTP_201_CREATED)

        except KeyError as e:
            return Response({
                "error": f"Champ requis manquant: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "error": f"Erreur lors de la création: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Login(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = get_user_by_email(email)
            jwt_token = jwt.encode({'account_id': user.account_id}, SECRET_KEY, algorithm='HS256')
            return Response({
                "token": jwt_token
            }, status=status.HTTP_200_OK)
        except Account.DoesNotExist:
            return Response({
                "error": "Identifiants invalides"
            }, status=status.HTTP_401_UNAUTHORIZED)

def get_user_by_email(email):
    if email.endswith("@student.efpl.be"):
        # Recherche dans les emails étudiants
        return Account.objects.get(studentEmail=email)
    elif email.endswith("@efpl.be"):
        # Recherche dans les emails employés
        return Account.objects.get(employeeEmail=email)
    else:
        raise ValueError("Format d'email invalide. Doit se terminer par @student.efpl.be ou @efpl.be")

