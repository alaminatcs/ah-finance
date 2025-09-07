from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'transaction_amount', 'balance_after_transaction', 'transaction_type', 'loan_approve_status']
    
    def save_model(self, request, obj, form, change):
        if obj.loan_approve_status and obj.transaction_type=='Loan Request':
            obj.account.balance += obj.transaction_amount
            obj.account.save()

            Transaction.objects.create(
                account = obj.account,
                transaction_type = 'Loan Given',
                transaction_amount = obj.transaction_amount,
                balance_after_transaction = obj.account.balance,
                loan_approve_status = True
            )
        
        super().save_model(request, obj, form, change)
