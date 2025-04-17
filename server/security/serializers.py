from rest_framework import serializers
from .models import Account, Student,  ContactDetails, Address

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ["password"]

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
        exclude = []


