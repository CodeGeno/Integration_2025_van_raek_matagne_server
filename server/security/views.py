# api/security/views.py
from rest_framework.views import APIView
from rest_framework import status
import string
import secrets
import bcrypt
from .decorators import jwt_required
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Student, ContactDetails, Address, Educator,Administrator
from .decorators import has_employee_role
from .entities.accountTypeEnum import EmployeRoleEnum
import jwt
from django.conf import settings
from .models import Account
import json
from .serializers import StudentSerializer
from api.models import ApiResponseClass
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q

SECRET_KEY = "264acbe227697c2106fec96de2608ffa9696eea8d4bec4234a4d49e099decc7448daafbc7ba2f4d7b127460936a200f9885c220e81c929525e310084a7abea6fc523f0b2a2241bc91899f158f4c437b059141ffc24642dfa2254842ae8acab96460e05a6293aea8a31f44aa860470b8d972d5f4d1adec181bf79d77fe4a2eed0eed7189da484c5601591ca222b11ff0ca56fce663f838cd4f1a5cddcec78f3821ac0da9769b848147238928f24d59849c7bb8dbf12697d214f04d7fbd476f38c3b360895b1e09d9c0d1291fd61452efb0616034baf32492550b3067d0a3adf317a6808da8555f1cffca990c0452e97d48c8becb77ccdda4290146c49b1c5a8b5"

class StudentCreationEndpoint(APIView):
    
    def post(self, request, *args, **kwargs):
        try:
            contact_details_data = request.data.get('contact_details')
            contact_details = ContactDetails.objects.create(**contact_details_data)

            address_data = request.data.get('address')
            address = Address.objects.create(**address_data)

            password_length = 12
            characters = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(characters) for _ in range(password_length))
         
            student = Student.objects.create(
                password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                contact_details=contact_details,
                address=address
            )
            student.save()
            student=Student.objects.select_related('contact_details','address').get(studentEmail=student.studentEmail)
            # Accéder aux détails de contact et à l'adresse
            contact_details = student.contact_details
            address = student.address

            # Vous pouvez maintenant utiliser contact_details et address
            print(contact_details.first_name, contact_details.last_name)
            print(address.street, address.city)
            serializer = StudentSerializer(student)
            return ApiResponseClass.created("Compte étudiant créé avec succès", serializer.data)

        except KeyError as e:
            return ApiResponseClass.error(f"Champ requis manquant: {str(e)}", status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la création: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
        

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
            
            return ApiResponseClass.created("Compte employé créé avec succès", {
                "employee_email": employee.employeeEmail,
                "employee_matricule": employee.matricule
            })

        except KeyError as e:
            return ApiResponseClass.error(f"Champ requis manquant: {str(e)}", status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la création: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)


class Login(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = get_user_by_email(email)
            jwt_token = jwt.encode({'account_id': user.account_id}, SECRET_KEY, algorithm='HS256')
            return ApiResponseClass.success("Token généré avec succès", {
                "token": jwt_token
            })
        except Account.DoesNotExist:
            return ApiResponseClass.unauthorized("Identifiants invalides")

def get_user_by_email(email):
    if email.endswith("@student.efpl.be"):
        # Recherche dans les emails étudiants
        return Account.objects.get(studentEmail=email)
    elif email.endswith("@efpl.be"):
        # Recherche dans les emails employés
        return Account.objects.get(employeeEmail=email)
    else:
        raise ValueError("Format d'email invalide. Doit se terminer par @student.efpl.be ou @efpl.be")

class CreateStudent(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Création des détails de contact
            contact_details = ContactDetails.objects.create(**request.data.get('contact_details'))
            
            # Création de l'adresse
            address = Address.objects.create(**request.data.get('address'))
            
            # Création de l'étudiant
            password_length = 12  # Longueur du mot de passe
            characters = string.ascii_letters + string.digits + string.punctuation
            password = ''.join(secrets.choice(characters) for _ in range(password_length))
            student = Student.objects.create(
                password=password,
                contact_details=contact_details,
                address=address
            )
            
            return ApiResponseClass.created("Compte étudiant créé avec succès", {
                "student_email": student.studentEmail
            })
            
        except KeyError as e:
            return ApiResponseClass.error(f"Champ requis manquant: {str(e)}", status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la création: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentPagination(PageNumberPagination):
    page_size = 10  # Nombre d'étudiants par page

@api_view(['GET'])
def StudentList(request):
    if request.method == 'GET':
        # Récupérer tous les étudiants
        students = Student.objects.all()

        # Recherche par nom ou email
        search_query = request.query_params.get('search', None)
        if search_query:
            students = students.filter(
                Q(contact_details__first_name__icontains=search_query) |
                Q(contact_details__last_name__icontains=search_query) |
                Q(studentEmail__icontains=search_query)
            )
  
        # Pagination
        paginator = StudentPagination()
        paginated_students = paginator.paginate_queryset(students, request)

        serializer = StudentSerializer(paginated_students, many=True)
        print(serializer.data)
        return ApiResponseClass.success("Liste des étudiants récupérée avec succès", serializer.data)  # Retourner la réponse paginée
