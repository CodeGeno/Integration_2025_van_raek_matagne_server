from django.db import models
from .entities.accountTypeEnum import GenderEnum, EmployeRoleEnum
from django.core.validators import RegexValidator
from datetime import datetime
from django.db.models import Q
import random

class ContactDetails(models.Model):
    contactDetailsId = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=50)
    lastName = models.CharField(max_length=50)
    phoneNumber = models.CharField(max_length=20)
    birthDate = models.DateField()
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
        lastContact = ContactDetails.objects.order_by('-identifier').first()
        
        if not lastContact or not lastContact.identifier:
            return "100000"
            
        lastNumber = int(lastContact.identifier)
        nextNumber = lastNumber + 1
        
        return str(nextNumber)

    def save(self, *args, **kwargs):
        if not self.identifier:
            self.identifier = self.generate_identifier()
        super().save(*args, **kwargs)

class Address(models.Model):
    addressId = models.AutoField(primary_key=True)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    zipCode = models.CharField(max_length=10)
    country = models.CharField(max_length=50)
    number = models.CharField(max_length=10)   
    complement = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50)

class Account(models.Model):
    accountId = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    password = models.CharField(max_length=128)
    contactDetails = models.OneToOneField(ContactDetails, on_delete=models.CASCADE, null=True, blank=True)
    address=models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)

    def generateEmail(self):
        base = f"{self.contactDetails.firstName.lower()}.{self.contactDetails.lastName.lower()}"
        domain = "@student.efpl.be" if isinstance(self, Student) else "@efpl.be"
        # Vérifier si l'email existe déjà
        counter = 1
        email = f"{base}{domain}"


        lastAccount = Account.objects.filter(
            email__startswith=base
        ).order_by('-email').first()
        if lastAccount:
            counter = int(lastAccount.email.split(base)[1].split(domain)[0]) + 1
        else:
            counter = 1

        email = f"{base}{counter}{domain}"          
        return email 
    

    def generateMatricule(self):
        genderDigit = '1' if self.contactDetails.gender == GenderEnum.MALE.value else '2'
        match self.contactDetails.gender:
            case GenderEnum.MALE.name:
                genderDigit = '1'
            case GenderEnum.FEMALE.name:
                genderDigit = '2'
            case _:
                raise ValueError("Genre invalide. Doit être 'Masculin' ou 'Féminin'")
            

        birthDate = self.contactDetails.birthDate
        
        # Convertir la date en string si elle est déjà un objet date
        if isinstance(birthDate, str):
            birthDate = datetime.strptime(birthDate, '%Y-%m-%d').date()
        
        birthStr = birthDate.strftime('%y%m%d')
        # Trouver un numéro unique en itérant sur les comptes existants
        baseMatricule = f"{genderDigit}{birthStr}"
        counter = 1
        while True:
            lastThree = f"{counter:03d}"  # Formatage sur 3 chiffres avec des zéros
            matriculeTest = f"{baseMatricule}{lastThree}"
            if not Account.objects.filter(
                Q(instructor__matricule=matriculeTest) | 
                Q(educator__matricule=matriculeTest)
            ).exists():
                break
            counter += 1
        return f"{genderDigit}{birthStr}{lastThree}"
    def save(self, *args, **kwargs):
       
        if not self.pk:  # Nouveau compte
            self.email = self.generateEmail()
                   
        super().save(*args, **kwargs)


class Student(Account): 
    pass




class Employee(Account):
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
            self.matricule = self.generateMatricule()
        super().save(*args, **kwargs)
    pass

