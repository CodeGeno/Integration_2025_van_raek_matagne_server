from django.db import models

gender_choices = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

from django.db import models

class Account(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    birthday = models.DateField()
    phone_number = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    address_id = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=gender_choices)


