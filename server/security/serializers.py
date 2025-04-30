from rest_framework import serializers
from .models import Account, Student, Employee, ContactDetails, Address

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ["password"]

class AccountCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = []

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class ContactDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactDetails
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    contactDetails = ContactDetailsSerializer()
    address = AddressSerializer()
    account = AccountSerializer(source='*')
    class Meta:
        model = Student
        exclude = ["password"]

class StudentCreationSerializer(serializers.ModelSerializer):
    contactDetails = ContactDetailsSerializer()
    address = AddressSerializer()
    class Meta:
        model = Student
        exclude = []

class EmployeeCreationSerializer(serializers.ModelSerializer):
    contactDetails = ContactDetailsSerializer()
    address = AddressSerializer()
    class Meta:
        model = Employee
        exclude = []

class EmployeeSerializer(serializers.ModelSerializer):
    contactDetails = ContactDetailsSerializer()
    address = AddressSerializer()
    class Meta:
        model = Employee
        exclude = ["password"]