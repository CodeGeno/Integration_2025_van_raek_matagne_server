# api/security/views.py
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.parsers import JSONParser
import string
import secrets
import bcrypt
from .decorators import jwt_required, checkRoleToken
from django.views.decorators.csrf import csrf_exempt
from .models import Student, ContactDetails, Address
from .entities.accountTypeEnum import AccountRoleEnum
from django.conf import settings
from .models import Account
import json
from .serializers import StudentSerializer,StudentCreationSerializer,EmployeeCreationSerializer,EmployeeSerializer
from api.models import ApiResponseClass
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination  
from django.db.models import Q
from api.pagination import StandardResultsSetPagination
from .models import Employee
import jwt
from django.http import JsonResponse

SECRET_KEY = "264acbe227697c2106fec96de2608ffa9696eea8d4bec4234a4d49e099decc7448daafbc7ba2f4d7b127460936a200f9885c220e81c929525e310084a7abea6fc523f0b2a2241bc91899f158f4c437b059141ffc24642dfa2254842ae8acab96460e05a6293aea8a31f44aa860470b8d972d5f4d1adec181bf79d77fe4a2eed0eed7189da484c5601591ca222b11ff0ca56fce663f838cd4f1a5cddcec78f3821ac0da9769b848147238928f24d59849c7bb8dbf12697d214f04d7fbd476f38c3b360895b1e09d9c0d1291fd61452efb0616034baf32492550b3067d0a3adf317a6808da8555f1cffca990c0452e97d48c8becb77ccdda4290146c49b1c5a8b5"

class StudentCreationEndpoint(APIView):
    parser_classes = [JSONParser]

    @checkRoleToken([AccountRoleEnum.EDUCATOR])
    def post(self, request):
        try:
            print("=== Début de la création d'un étudiant ===")
            print("Données reçues:", request.data)
            
            contactDetails_data = request.data.get('contactDetails')
            contactDetails = ContactDetails.objects.create(**contactDetails_data)
                
            address_data = request.data.get('address')
            address = Address.objects.create(**address_data)

            password_length = 12
            characters = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(characters) for _ in range(password_length))
         
            student = Student.objects.create(
                password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                contactDetails=contactDetails,
                address=address
            )
            student.save()
            student = Student.objects.select_related('contactDetails','address').get(email=student.email)

            serializer = StudentCreationSerializer(student)
            return ApiResponseClass.created("Compte étudiant créé avec succès", {**serializer.data, "password": password})

        except KeyError as e:
            print("ERREUR: Champ manquant:", str(e))
            return ApiResponseClass.error(f"Champ requis manquant: {str(e)}", status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print("ERREUR: Exception lors de la création:", str(e))
            return ApiResponseClass.error(f"Erreur lors de la création: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmployeeCreationEndpoint(APIView):
    parser_classes = [JSONParser]

    @checkRoleToken([AccountRoleEnum.ADMINISTRATOR])
    def post(self, request):
        try:
            contactDetails_data = request.data.get('contactDetails')
            contactDetails = ContactDetails.objects.create(**contactDetails_data)

            address_data = request.data.get('address')
            address = Address.objects.create(**address_data)
            
            password_length = 12
            characters = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(characters) for _ in range(password_length))
            employee_role = request.data.get('role')
            
            if employee_role not in [role.name for role in AccountRoleEnum]:
                return ApiResponseClass.error(f"Rôle d'employé invalide: {employee_role}", status.HTTP_400_BAD_REQUEST)
            
            employee = Employee.objects.create(
                contactDetails=contactDetails,
                password=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                address=address,
                role=AccountRoleEnum[employee_role].value
            )
            employee.password=password
            serializer = EmployeeCreationSerializer(employee)
            return ApiResponseClass.created("Compte employé créé avec succès", serializer.data)

        except KeyError as e:
            return ApiResponseClass.error(f"Champ requis manquant: {str(e)}", status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la création: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

class Login(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user, user_type, user_role = get_user_by_email(email)
            
            payload = {
                'accountId': user.id
            }
            jwt_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            
            response_data = {
                "token": jwt_token,
                "role": get_enum_name_by_value(AccountRoleEnum, user_role)
            }
           
            return ApiResponseClass.success("Token généré avec succès", response_data)
        except Account.DoesNotExist:
            return ApiResponseClass.unauthorized("Identifiants invalides")

class StudentList(APIView):
    parser_classes = [JSONParser]

    @checkRoleToken([AccountRoleEnum.ADMINISTRATOR, AccountRoleEnum.EDUCATOR])
    def get(self, request):
        print(request.COOKIES)
        students = Student.objects.all().order_by('id')

        search_query = request.query_params.get('search', None)
        if search_query:
            students = students.filter(
                Q(contactDetails__firstName__icontains=search_query) |
                Q(contactDetails__lastName__icontains=search_query) |
                Q(email__icontains=search_query)
            )

        paginator = StandardResultsSetPagination()  
        paginated_students = paginator.paginate_queryset(students, request)
        serializer = StudentSerializer(paginated_students, many=True)
        
        return ApiResponseClass.succesOverview(
            "Liste des étudiants récupérée avec succès", 
            serializer.data, 
            paginator.page.number, 
            paginator.page.paginator.num_pages
        )

class EmployeeList(APIView):
    parser_classes = [JSONParser]

    @checkRoleToken([AccountRoleEnum.ADMINISTRATOR])
    def get(self, request):
        print(request.COOKIES)
        employees = Employee.objects.all().order_by('id')
        
        search_query = request.query_params.get('search', None)
        if search_query:
            employees = employees.filter(
                Q(contactDetails__firstName__icontains=search_query) |
                Q(contactDetails__lastName__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(role__icontains=search_query) |
                Q(matricule__icontains=search_query)
            )

        paginator = StandardResultsSetPagination()  
        paginated_employees = paginator.paginate_queryset(employees, request)
        serializer = EmployeeSerializer(paginated_employees, many=True)
        
        return ApiResponseClass.succesOverview(
            "Liste des employés récupérée avec succès", 
            serializer.data, 
            paginator.page.number, 
            paginator.page.paginator.num_pages
        )

class EmployeeEdit(APIView):
    parser_classes = [JSONParser]

    def patch(self, request, employee_id):
        try:
            employee = Employee.objects.get(id=employee_id)
            data = request.data
            
            if 'contactDetails' in data:
                contact_data = data.get('contactDetails')
                for key, value in contact_data.items():
                    setattr(employee.contactDetails, key, value)
                employee.contactDetails.save()
                
            if 'address' in data:
                address_data = data.get('address')
                for key, value in address_data.items():
                    setattr(employee.address, key, value)
                employee.address.save()
            
            if 'role' in data:
                role = data.get('role')
                if role in [role.name for role in AccountRoleEnum]:
                    employee.role = AccountRoleEnum[role].value
                else:
                    return ApiResponseClass.error(
                        f"Rôle d'employé invalide: {role}", 
                        status.HTTP_400_BAD_REQUEST
                    )
            
            employee.save()
            serializer = EmployeeSerializer(employee)
            return ApiResponseClass.success("Employé mis à jour avec succès", serializer.data)
            
        except Employee.DoesNotExist:
            return ApiResponseClass.error("Employé non trouvé", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la mise à jour: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmployeeGetById(APIView):
    parser_classes = [JSONParser]

    def get(self, request, employee_id):
        try:
            employee = Employee.objects.get(id=employee_id)
            serializer = EmployeeSerializer(employee)
            return ApiResponseClass.success("Employé récupéré avec succès", serializer.data)
        except Employee.DoesNotExist:
            return ApiResponseClass.error("Employé non trouvé", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la récupération: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentGetById(APIView):
    parser_classes = [JSONParser]

    def get(self, request, id):
        try:
            student = Student.objects.get(id=id)
            serializer = StudentSerializer(student)
            return ApiResponseClass.success("Étudiant récupéré avec succès", serializer.data)
        except Student.DoesNotExist:
            return ApiResponseClass.error("Étudiant non trouvé", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la récupération: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

class StudentEdit(APIView):
    parser_classes = [JSONParser]

    def patch(self, request, student_id):
        try:
            student = Student.objects.get(id=student_id)
            data = request.data
            
            if 'contactDetails' in data:
                contact_data = data.get('contactDetails')
                for key, value in contact_data.items():
                    setattr(student.contactDetails, key, value)
                student.contactDetails.save()
                
            if 'address' in data:
                address_data = data.get('address')
                for key, value in address_data.items():
                    setattr(student.address, key, value)
                student.address.save()
            
            student.save()
            serializer = StudentSerializer(student)
            return ApiResponseClass.success("Étudiant mis à jour avec succès", serializer.data)
            
        except Student.DoesNotExist:
            return ApiResponseClass.error("Étudiant non trouvé", status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la mise à jour: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

class EmployeeTeacherList(APIView):
    parser_classes = [JSONParser]

    def get(self, request):
        try:
            teachers = Employee.objects.filter(role=AccountRoleEnum.PROFESSOR.value)
            serializer = EmployeeSerializer(teachers, many=True)
            return ApiResponseClass.success("Liste des professeurs récupérée avec succès", serializer.data)
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la récupération des professeurs: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_enum_name_by_value(enum_class, value):
    for name, member in enum_class.__members__.items():
        if member.value == value:
            print(name)
            return name
    return None

def get_user_by_email(email):
    try:
        user = Account.objects.get(email=email)
        if email.endswith("@efpl.be"):
            return user, "employee", getattr(user.employee, 'role', None) if hasattr(user, 'employee') else None
        else:
            return user, "student", None
    except Account.DoesNotExist:
        raise Account.DoesNotExist("Aucun compte trouvé avec cet email")

