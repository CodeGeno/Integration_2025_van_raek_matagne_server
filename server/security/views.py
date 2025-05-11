# api/security/views.py
from rest_framework.views import APIView
from rest_framework import status
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
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination  
from django.db.models import Q
from api.pagination import StandardResultsSetPagination
from .models import Employee
import jwt


SECRET_KEY = "264acbe227697c2106fec96de2608ffa9696eea8d4bec4234a4d49e099decc7448daafbc7ba2f4d7b127460936a200f9885c220e81c929525e310084a7abea6fc523f0b2a2241bc91899f158f4c437b059141ffc24642dfa2254842ae8acab96460e05a6293aea8a31f44aa860470b8d972d5f4d1adec181bf79d77fe4a2eed0eed7189da484c5601591ca222b11ff0ca56fce663f838cd4f1a5cddcec78f3821ac0da9769b848147238928f24d59849c7bb8dbf12697d214f04d7fbd476f38c3b360895b1e09d9c0d1291fd61452efb0616034baf32492550b3067d0a3adf317a6808da8555f1cffca990c0452e97d48c8becb77ccdda4290146c49b1c5a8b5"

class StudentCreationEndpoint(APIView):
    @checkRoleToken([AccountRoleEnum.ADMINISTRATOR,AccountRoleEnum.EDUCATOR])
    def post(self, request, *args, **kwargs):
        try:
            print(request.data)
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
            student=Student.objects.select_related('contactDetails','address').get(email=student.email)
            # Vous pouvez maintenant utiliser contact_details et address
    
            serializer = StudentCreationSerializer(student)
            return ApiResponseClass.created("Compte étudiant créé avec succès", {**serializer.data,"password":password})

        except KeyError as e:
            return ApiResponseClass.error(f"Champ requis manquant: {str(e)}", status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return ApiResponseClass.error(f"Erreur lors de la création: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EmployeeCreationEndpoint(APIView):
   # @checkRoleToken([AccountRoleEnum.ADMINISTRATOR])
    def post(self, request, *args, **kwargs):
        try:
            # Créer d'abord les détails de contact
            contactDetails_data = request.data.get('contactDetails')
            contactDetails = ContactDetails.objects.create(**contactDetails_data)

            # Créer l'adresse
            address_data = request.data.get('address')
            address = Address.objects.create(**address_data)
            
            password_length = 12
            characters = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(characters) for _ in range(password_length))
            # Créer l'employé avec le rôle spécifié
            employee_role = request.data.get('role')
            
            # Vérifier que le rôle est valide
            if employee_role not in [role.name for role in AccountRoleEnum]:
                return ApiResponseClass.error(f"Rôle d'employé invalide: {employee_role}", status.HTTP_400_BAD_REQUEST)
            
            # Créer l'employé avec le modèle générique Employee
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

def get_enum_name_by_value(enum_class, value):
    for name, member in enum_class.__members__.items():
        if member.value == value:
            print(name)
            return name
    return None

class Login(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user, user_type, user_role = get_user_by_email(email)
            
            # Créer le payload du token  
            payload = {
                'accountId': user.id
            }
            jwt_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
            
            # Construire la réponse
            response_data = {
                "token": jwt_token,
                "role": get_enum_name_by_value(AccountRoleEnum, user_role)
            }
           
            return ApiResponseClass.success("Token généré avec succès", response_data)
        except Account.DoesNotExist:
            return ApiResponseClass.unauthorized("Identifiants invalides")

def get_user_by_email(email):
    try:
        # Rechercher l'utilisateur par son email, qui est maintenant un champ unique dans le modèle Account
        user = Account.objects.get(email=email)
        
        # Déterminer le type d'utilisateur en fonction du domaine de l'email
        if email.endswith("@efpl.be"):
            # Pour les employés
            return user, "employee", getattr(user.employee, 'role', None) if hasattr(user, 'employee') else None
        else:
            # Pour les étudiants
            return user, "student", None
            
    except Account.DoesNotExist:
        raise Account.DoesNotExist("Aucun compte trouvé avec cet email")

@api_view(['GET'])
def StudentList(request):
    print(request.COOKIES)
    if request.method == 'GET':
        # Récupérer tous les étudiants
        students = Student.objects.all().order_by('id')  # Utiliser le nom correct du champ en base de données

        # Recherche par nom ou email
        search_query = request.query_params.get('search', None)
        if search_query:
            students = students.filter(
                Q(contactDetails__firstName__icontains=search_query) |
                Q(contactDetails__lastName__icontains=search_query) |
                Q(email__icontains=search_query)
            )
  
        # Pagination
        paginator = StandardResultsSetPagination()  
        paginated_students = paginator.paginate_queryset(students, request)
        serializer = StudentSerializer(paginated_students, many=True)
        
        # Obtenir les informations de pagination correctement
        return ApiResponseClass.succesOverview(
            "Liste des étudiants récupérée avec succès", 
            serializer.data, 
            paginator.page.number, 
            paginator.page.paginator.num_pages
        )

@api_view(['GET'])
def EmployeeList(request):
    print(request.COOKIES)
    if request.method == 'GET':
        # Récupérer tous les employés
        employees = Employee.objects.all().order_by('id')  # Utiliser le nom correct du champ en base de données
        
        # Recherche par nom ou email
        search_query = request.query_params.get('search', None)
        if search_query:
            employees = employees.filter(
                Q(contactDetails__firstName__icontains=search_query) |
                Q(contactDetails__lastName__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(role__icontains=search_query) |
                Q(matricule__icontains=search_query)
            )
  
        # Pagination
        paginator = StandardResultsSetPagination()  
        paginated_employees = paginator.paginate_queryset(employees, request)
        serializer = EmployeeSerializer(paginated_employees, many=True)
        
        # Obtenir les informations de pagination correctement
        return ApiResponseClass.succesOverview(
            "Liste des employés récupérée avec succès", 
            serializer.data, 
            paginator.page.number, 
            paginator.page.paginator.num_pages
        )
    
@api_view(['PATCH'])
def EmployeeEdit(request, employee_id):
    try:
       
        # Récupérer l'employé par ID
        employee = Employee.objects.get(id=employee_id)
        
        # Mise à jour des informations de l'employé
        # Récupérer les données du corps de la requête
        data = request.data
        
        # Mise à jour des informations de contact
        if 'contactDetails' in data:
            contact_data = data.get('contactDetails')
            for key, value in contact_data.items():
                setattr(employee.contactDetails, key, value)
            employee.contactDetails.save()
            
        # Mise à jour des informations d'adresse
        if 'address' in data:
            address_data = data.get('address')
            for key, value in address_data.items():
                setattr(employee.address, key, value)
            employee.address.save()
        
        # Mise à jour du rôle si présent
        if 'role' in data:
            role = data.get('role')
            if role in [role.name for role in AccountRoleEnum]:
                employee.role = AccountRoleEnum[role].value
            else:
                return ApiResponseClass.error(
                    f"Rôle d'employé invalide: {role}", 
                    status.HTTP_400_BAD_REQUEST
                )
        
        # Sauvegarder les modifications
        employee.save()
        
        # Sérialiser les données mises à jour
        serializer = EmployeeSerializer(employee)
        
        # Retourner les données sérialisées
        return ApiResponseClass.success(
            "Informations de l'employé mises à jour avec succès", 
            serializer.data
        )
    except Employee.DoesNotExist:
        return ApiResponseClass.error(
            "Employé non trouvé", 
            status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(e)
        return ApiResponseClass.error(
            f"Erreur lors de la mise à jour de l'employé: {str(e)}", 
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
def EmployeeGetById(request, employee_id):
    try:
        # Récupérer l'employé par ID
        employee = Employee.objects.get(id=employee_id)
        
        # Sérialiser les données de l'employé
        serializer = EmployeeSerializer(employee)
        print(serializer.data)
        # Retourner les données sérialisées
        return ApiResponseClass.success(
            "Détails de l'employé récupérés avec succès", 
            serializer.data
        )
    except Employee.DoesNotExist:
        return ApiResponseClass.error(
            "Employé non trouvé", 
            status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return ApiResponseClass.error(
            f"Erreur lors de la récupération de l'employé: {str(e)}", 
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
def StudentGetById(request, id):
    try:
        # Récupérer l'étudiant par ID
        student = Student.objects.get(id=id)
        
        # Sérialiser les données de l'étudiant
        serializer = StudentSerializer(student)
        print(serializer.data)
        # Retourner les données sérialisées
        return ApiResponseClass.success(
            "Détails de l'étudiant récupérés avec succès", 
            serializer.data
        )
    except Student.DoesNotExist:
        return ApiResponseClass.error(
            "Étudiant non trouvé", 
            status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return ApiResponseClass.error(
            f"Erreur lors de la récupération de l'étudiant: {str(e)}", 
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['PATCH'])
def StudentEdit(request, student_id):
    try:
        # Récupérer l'étudiant par ID
        student = Student.objects.get(id=student_id)
        
        # Mise à jour des informations de l'étudiant
        # Récupérer les données du corps de la requête
        data = request.data
        
        # Mise à jour des informations de contact
        if 'contactDetails' in data:
            contact_data = data.get('contactDetails')
            for key, value in contact_data.items():
                setattr(student.contactDetails, key, value)
            student.contactDetails.save()
            
        # Mise à jour des informations d'adresse
        if 'address' in data:
            address_data = data.get('address')
            for key, value in address_data.items():
                setattr(student.address, key, value)
            student.address.save()
        
        # Mise à jour du rôle si présent (bien que cela soit normalement fixé pour un étudiant)
        if 'role' in data:
            role = data.get('role')
            if role in [role.name for role in AccountRoleEnum]:
                student.role = AccountRoleEnum[role].value
            else:
                return ApiResponseClass.error(
                    f"Rôle d'étudiant invalide: {role}", 
                    status.HTTP_400_BAD_REQUEST
                )
        
        # Sauvegarder les modifications
        student.save()
        
        # Sérialiser les données mises à jour
        serializer = StudentSerializer(student)
        
        # Retourner les données sérialisées
        return ApiResponseClass.success(
            "Informations de l'étudiant mises à jour avec succès", 
            serializer.data
        )
    except Student.DoesNotExist:
        return ApiResponseClass.error(
            "Étudiant non trouvé", 
            status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(e)
        return ApiResponseClass.error(
            f"Erreur lors de la mise à jour de l'étudiant: {str(e)}", 
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@api_view(['GET'])
def EmployeeTeacherList(request):
    if request.method == 'GET':
        # Récupérer uniquement les employés avec le rôle 'PROFESSOR'
        teachers = Employee.objects.filter(role=AccountRoleEnum.PROFESSOR.value).order_by('id')
        
        # Recherche par nom ou email
        search_query = request.query_params.get('search', None)
        if search_query:
            teachers = teachers.filter(
                Q(contactDetails__firstName__icontains=search_query) |
                Q(contactDetails__lastName__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(matricule__icontains=search_query)
            )
  
        # Pagination
        paginator = StandardResultsSetPagination()  
        paginated_teachers = paginator.paginate_queryset(teachers, request)
        serializer = EmployeeSerializer(paginated_teachers, many=True)
        
        # Obtenir les informations de pagination correctement
        return ApiResponseClass.succesOverview(
            "Liste des professeurs récupérée avec succès", 
            serializer.data, 
            paginator.page.number, 
            paginator.page.paginator.num_pages
        )

