import environ
env = environ.Env()
from django.contrib import admin
from .models import Transaction
from django.core.mail import send_mail
from django.contrib.humanize.templatetags.humanize import intcomma

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'transaction_amount', 'balance_after_transaction', 'transaction_type', 'loan_approve_status']
    
    def save_model(self, request, obj, form, change):
        if obj.loan_approve_status and obj.transaction_type=='Loan Request':
            obj.account.balance += obj.transaction_amount
            obj.account.save()

            # create a transaction for given loan
            loan = Transaction.objects.create(
                account = obj.account,
                transaction_type = 'Loan Given',
                transaction_amount = obj.transaction_amount,
                balance_after_transaction = obj.account.balance,
                loan_approve_status = True
            )

            # transaction mail send
            send_mail(
                subject = 'Transaction Type - Loan Given',
                from_email = env('EMAIL_HOST_USER'),
                recipient_list = [obj.account.user.email, ],

                message = f'''
                Hello {obj.account.user.first_name},
                You're Loan request Approved by Admin.
                    -Loan Id: {loan.id}
                    -Loan Amount Given: ${intcomma(loan.transaction_amount)}
                    -Balance After Loan Revceived: ${intcomma(loan.balance_after_transaction)}
                __
                Regards,
                AH-Finance'''
            )
        
        super().save_model(request, obj, form, change)
