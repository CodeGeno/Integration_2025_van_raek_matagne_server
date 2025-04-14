from django.db import models
from .entities.accountTypeEnum import GenderEnum, EmployeRoleEnum
from django.core.validators import RegexValidator
from datetime import datetime
from django.db.models import Q
import random

class ContactDetails(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    birth_date = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=[(gender.value, gender.name) for gender in GenderEnum],
        default=GenderEnum.MALE.value 
    )
    identifier = models.CharField(
        max_length=6,
        unique=True,
        validators=[
            RegexValidator(
                regex='^[1-9][0-9]{5}$',
                message='L\'identifiant doit être composé de 6 chiffres et ne pas commencer par 0'
            )
        ]
    )
    
    def generate_identifier(self):
        # Récupérer le dernier identifiant utilisé
        last_contact = ContactDetails.objects.order_by('-identifier').first()
        
        if not last_contact or not last_contact.identifier:
            return "100000"
            
        last_number = int(last_contact.identifier)
        next_number = last_number + 1
        
        return str(next_number)

    def save(self, *args, **kwargs):
        if not self.identifier:
            self.identifier = self.generate_identifier()
        super().save(*args, **kwargs)

class Address(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50)
    number = models.CharField(max_length=10)   
    complement = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50)

class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    employee_email = models.EmailField(unique=True, null=True, blank=True)
    student_email = models.EmailField(unique=True, null=True, blank=True)
    password = models.CharField(max_length=128)
    employee_role = models.CharField(
        max_length=20,
        choices=[(employe_role.value, employe_role.name) for employe_role in EmployeRoleEnum],
        default=EmployeRoleEnum.PROFESSOR.value 
    )
    contact_details = models.OneToOneField(ContactDetails, on_delete=models.CASCADE, null=True, blank=True)
    address=models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)

    def generate_email(self):
        base = f"{self.contact_details.first_name.lower()}.{self.contact_details.last_name.lower()}"
        domain = "@student.efpl.be" if isinstance(self, Student) else "@efpl.be"
        
        # Vérifier si l'email existe déjà
        counter = 1
        email = f"{base}{domain}"
        
        while True:
            if isinstance(self, Student):
                exists = Account.objects.filter(studentEmail=email).exists()
            else:
                exists = Account.objects.filter(employeeEmail=email).exists()
                
            if not exists:
                break
                
            counter += 1
            email = f"{base}{counter}{domain}"          
        return email 
    def generate_matricule(self):
        gender_digit = '1' if self.contact_details.gender == GenderEnum.MALE.value else '2'
        match self.contact_details.gender:
            case GenderEnum.MALE.name:
                gender_digit = '1'
            case GenderEnum.FEMALE.name:
                gender_digit = '2'
            case _:
                raise ValueError("Genre invalide. Doit être 'Masculin' ou 'Féminin'")
            

        birth_date = self.contact_details.birth_date
        
        # Convertir la date en string si elle est déjà un objet date
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        
        birth_str = birth_date.strftime('%y%m%d')
        # Trouver un numéro unique en itérant sur les comptes existants
        base_matricule = f"{gender_digit}{birth_str}"
        counter = 1
        while True:
            last_three = f"{counter:03d}"  # Formatage sur 3 chiffres avec des zéros
            matricule_test = f"{base_matricule}{last_three}"
            if not Account.objects.filter(
                Q(instructor__matricule=matricule_test) | 
                Q(educator__matricule=matricule_test)
            ).exists():
                break
            counter += 1
        return f"{gender_digit}{birth_str}{last_three}"
    def save(self, *args, **kwargs):
       
        if not self.pk:  # Nouveau compte
            if isinstance(self, (Instructor, Educator)):
                self.employeeEmail = self.generate_email()
            if isinstance(self, Student):
                print("We are here")
                self.studentEmail = self.generate_email()
        super().save(*args, **kwargs)

class Instructor(Account):  
    matricule = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[12]\d{8}$',
                message='Format matricule invalide'
            )
        ]
    )
    
    def save(self, *args, **kwargs):
        if not self.matricule:
            self.matricule = self.generate_matricule()
        super().save(*args, **kwargs)


class Student(Account): 
    pass

class Educator(Account):
    matricule = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[12]\d{8}$',
                message='Format matricule invalide'
            )
        ]
    )
    
    def save(self, *args, **kwargs):
        if not self.matricule:
            self.matricule = self.generate_matricule()
        super().save(*args, **kwargs)

class Administrator(Account):
    matricule = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex='^[12]\d{8}$',
                message='Format matricule invalide'
            )
        ]
    )
    def save(self, *args, **kwargs):
        if not self.matricule:
            self.matricule = self.generate_matricule()
        super().save(*args, **kwargs)

