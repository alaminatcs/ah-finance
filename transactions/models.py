from django.db import models
from accounts.models import UserBankAccount
from .constants import TRANSACTION_TYPE

# Create your models here.
class Transaction(models.Model):
    account = models.ForeignKey(UserBankAccount, on_delete=models.CASCADE, related_name='transactions')
    
    transaction_time = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    transaction_amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after_transaction = models.DecimalField(max_digits=12, decimal_places=2)
    loan_approve_status = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-transaction_time']