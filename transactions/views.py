import datetime
import environ
env = environ.Env()
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import send_mail
from transactions.models import Transaction
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, CreateView, ListView
from django.contrib.humanize.templatetags.humanize import intcomma
from transactions.forms import DepositForm, WithdrawForm, LoanRequestForm

# parent class for all type of transactions view
class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transactions:transaction_report')
    title = ''

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['account'] = self.request.user.account
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context

# deposit view
class DepositView(TransactionCreateView):
    form_class = DepositForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transaction_type': 'Deposit'}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data['transaction_amount']
        self.request.user.account.balance += amount
        self.request.user.account.save(update_fields = ['balance'])

        response = super().form_valid(form)

        # send deposit mail
        send_mail(
            subject = 'Transaction Type - Deposit',
            from_email = env('EMAIL_HOST_USER'),
            recipient_list = [self.request.user.email, ],
            
            message = f'''
            Hello {self.request.user.first_name},
            You've successfully deposited ${intcomma(amount)} into your account.
                -Balance After Transaction: ${intcomma(self.request.user.account.balance)}
            __
            Regards,
            AH-Finance'''
        )
        
        return response

# withdraw view
class WithdrawView(TransactionCreateView):
    form_class = WithdrawForm
    title = 'Withdraw'

    def get_initial(self):
        initial = {'transaction_type': 'Withdraw'}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data['transaction_amount']
        self.request.user.account.balance -= amount
        self.request.user.account.save(update_fields=['balance'])

        response = super().form_valid(form)
        
        # send withdraw mail
        send_mail(
            subject = 'Transaction Type - Withdraw',
            from_email = env('EMAIL_HOST_USER'),
            recipient_list = [self.request.user.email, ],
            
            message = f'''
            Hello {self.request.user.first_name},
            You've successfully withdrawn ${intcomma(amount)} from your account.
                -Balance After Transaction: ${intcomma(self.request.user.account.balance)}
            __
            Regards,
            AH-Finance''',
        )

        return response

# loan request view
class LoanRequestView(TransactionCreateView):
    form_class = LoanRequestForm
    title = 'Loan Request'

    def get_initial(self):
        initial = {'transaction_type': 'Loan Request'}
        return initial

    def form_valid(self, form):
        no_of_pending_loan = Transaction.objects.filter(
            account=self.request.user.account,
            transaction_type='Loan Given', loan_approve_status=True
        ).count()

        if no_of_pending_loan >= 2:
            messages.error(self.request, "You've already 2 pending Loan!")
            return redirect('transactions:loan_list')
        
        response = super().form_valid(form)
        
        # send loan request mail
        send_mail(
            subject = 'Transaction Type - Loan Request',
            from_email = env('EMAIL_HOST_USER'),
            recipient_list = [self.request.user.email, ],

            message = f'''
            Hello {self.request.user.first_name},
            You're Loan request sent to Admin.
                -Requested Loan Amount: ${intcomma(self.object.transaction_amount)}
            __
            Regards,
            AH-Finance'''
        )
        # messages.success(self.request, "You're Loan request sent to the Admin") 

        return response

# transaction report view
class TransactionReportView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/transaction_report.html'
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(account=self.request.user.account)
        
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        # if date range filter applied
        if start_date_str and end_date_str:
            start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            queryset = queryset.filter(
                transaction_time__date__gte = start_date,
                transaction_time__date__lte = end_date
            )
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['account']  = self.request.user.account
        return context

# loan list view
class LoanListView(LoginRequiredMixin,ListView):
    model = Transaction
    template_name = 'transactions/loan_request.html'
    
    def get_queryset(self):
        user_account = self.request.user.account
        # queryset = Transaction.objects.filter(account=user_account, transaction_type__in=['Loan Request', 'Loan Given'])
        queryset = Transaction.objects.filter(account=user_account, transaction_type__icontains='Loan')
        return queryset

# loan pay view
class LoanPayView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        if loan.loan_approve_status and loan.transaction_type=='Loan Given':
            user_account = loan.account
            if loan.transaction_amount <= user_account.balance:
                user_account.balance -= loan.transaction_amount
                user_account.save()

                # create a transaction for loan paid
                Transaction.objects.create(
                    account = user_account,
                    transaction_type = 'Loan Paid',
                    transaction_amount = loan.transaction_amount,
                    balance_after_transaction = user_account.balance,
                    loan_approve_status = True
                )

                # send loan paid mail
                send_mail(
                    subject = 'Transaction Type - Loan Paid',
                    from_email = env('EMAIL_HOST_USER'),
                    recipient_list = [self.request.user.email, ],

                    message = f'''
                    Hello {self.request.user.first_name},
                    You've Paid ${intcomma(loan.transaction_amount)} for Loan Id-{loan_id}.
                        -Balance After Loan Paid: ${intcomma(user_account.balance)}
                    __
                    Regards,
                    AH-Finance'''
                )
                # messages.success(self.request, "Loan paid successfully!")

                loan.loan_approve_status = False
                loan.save()
            else:
                messages.error(request, 'Remains not enough balance to pay Loan!')
        
        return redirect('transactions:loan_list')