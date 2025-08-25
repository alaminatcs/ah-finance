from django.db import models
from django.contrib.auth.models import User
from .constants import ACCOUNT_TYPE, GENDER_TYPE

# User Account info
class UserBankAccount(models.Model):
    user = models.OneToOneField(User, related_name='account', on_delete=models.CASCADE)
    gender = models.CharField(max_length=20, choices=GENDER_TYPE)
    birth_date = models.DateField(null=True, blank=True)
    account_no = models.IntegerField(unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE)
    initial_deposite_date = models.DateField(auto_now_add=True)
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.user} - {self.user.first_name}"

# User Address info    
class UserAddress(models.Model):
    user = models.OneToOneField(User, related_name='address', on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    postal_code = models.IntegerField()
    city = models.CharField(max_length= 100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user} - {self.user.first_name}"