from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'transaction_amount', 'balance_after_transaction', 'transaction_type', 'loan_approve_status']
    
    def save_model(self, request, obj, form, change):
        obj.account.balance += obj.transaction_amount
        obj.balance_after_transaction = obj.account.balance
        obj.account.save()
        super().save_model(request, obj, form, change)
