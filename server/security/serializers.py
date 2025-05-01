from rest_framework import serializers
from .models import Account, Student, Employee, ContactDetails, Address ,AccountRoleEnum,GenderEnum

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
    gender_name = serializers.SerializerMethodField()
    def get_gender_name(self, obj):
        # Trouver l'énumération correspondant à la valeur stockée
        for gender_enum in GenderEnum:
            if gender_enum.value == obj.gender:
                return gender_enum.name
        return None
    class Meta:
        model = ContactDetails
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    def get_role(self, obj):
           # Trouver l'énumération correspondant à la valeur stockée
           for role_enum in AccountRoleEnum:
               if role_enum.value == obj.role:
                   return role_enum.name
           return None
    contactDetails = ContactDetailsSerializer()
    address = AddressSerializer()
    account = AccountSerializer(source='*')
    class Meta:
        model = Student
        exclude = ["password"]

class StudentCreationSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    def get_role(self, obj):
           # Trouver l'énumération correspondant à la valeur stockée
           for role_enum in AccountRoleEnum:
               if role_enum.value == obj.role:
                   return role_enum.name
           return None
    contactDetails = ContactDetailsSerializer()
    address = AddressSerializer()
    class Meta:
        model = Student
        exclude = []

class EmployeeCreationSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    def get_role(self, obj):
           # Trouver l'énumération correspondant à la valeur stockée
           for role_enum in AccountRoleEnum:
               if role_enum.value == obj.role:
                   return role_enum.name
           return None
    contactDetails = ContactDetailsSerializer()
    address = AddressSerializer()
    class Meta:
        model = Employee
        exclude = []

class EmployeeSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    def get_role(self, obj):
           # Trouver l'énumération correspondant à la valeur stockée
           for role_enum in AccountRoleEnum:
               if role_enum.value == obj.role:
                   return role_enum.name
           return None
    contactDetails = ContactDetailsSerializer()
    address = AddressSerializer()
    class Meta:
        model = Employee
        exclude = ["password"]