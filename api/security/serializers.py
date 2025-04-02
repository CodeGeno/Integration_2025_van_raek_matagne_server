from rest_framework import serializers
from .models import Account, Instructor, Student, Administrator, ContactDetails, Address

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = '__all__'
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
class ContactDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactDetails
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    contact_details = ContactDetailsSerializer()
    address = AddressSerializer()
    class Meta:
        model = Student
        exclude = ["employeeEmail", "employee_role"]

class AdministratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrator
        fields = '__all__'


