from django.db import models
from .entities.accountTypeEnum import GenderEnum  


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
    
class Address(models.Model):
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=50)
    number = models.CharField(max_length=10)   

class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    account_type = models.CharField(max_length=50)
    contact_details = models.OneToOneField(ContactDetails, on_delete=models.CASCADE, null=True, blank=True)
    address=models.OneToOneField(Address, on_delete=models.CASCADE, null=True, blank=True)

class Instructor(Account):  
    matricule = models.CharField(max_length=20)


class Student(Account): 
    pass

class Educator(Account):
    matricule = models.CharField(max_length=20)
    is_administrator = models.BooleanField(default=False)
    pass


