from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib import messages
from transactions.models import Transaction
from django.views.generic import View, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from transactions.forms import DepositForm, WithdrawForm, LoanRequestForm
import datetime
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import models

class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('transaction_report')
    title = ''

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['account'] = self.request.user.account
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context

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
        
        messages.success(self.request, f"You've deposit ${amount} successfully.")
        
        return super().form_valid(form)

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

        messages.success(self.request, f'Successfully withdrawn {"{:,.2f}".format(float(amount))}$ from your account')
        
        return super().form_valid(form)

class LoanRequestView(TransactionCreateView):
    form_class = LoanRequestForm
    title = 'Loan Request'

    def get_initial(self):
        initial = {'transaction_type': 'Loan Request'}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data['transaction_amount']
        current_loan_count = Transaction.objects.filter(
            account=self.request.user.account,
            transaction_type='Loan Request',
            loan_approve_status = True
        ).count()

        if current_loan_count >= 3:
            return HttpResponse("You have cross the loan limits")
            # return messages.info(self.request, "You have cross the loan limits")
        
        messages.success(self.request, f'Loan request for ${amount} submitted successfully')
        
        return super().form_valid(form)
    
class TransactionReportView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transactions/transaction_report.html'
    balance = 0 # filter korar pore ba age amar total balance ke show korbe
    
    def get_queryset(self):
        queryset = super().get_queryset().filter(account=self.request.user.account)
        
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            queryset = queryset.filter(
                transaction_time__date__gte = start_date,
                transaction_time__date__lte = end_date
            )
            self.balance = Transaction.objects.filter(
                transaction_time__date__gte = start_date,
                transaction_time__date__lte = end_date
            ).aggregate(total=models.Sum('transaction_amount'))['total']
            # self.balance = queryset.aggregate(total=Transaction.Sum('transaction_amount'))['total']
        else:
            self.balance = self.request.user.account.balance
       
        return queryset.distinct() # unique queryset hote hobe
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['account']  = self.request.user.account
        return context

class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)
        # print(loan)
        if loan.loan_approve_status:
            user_account = loan.account
                # Reduce the loan amount from the user's balance
                # 5000, 500 + 5000 = 5500
                # balance = 3000, loan = 5000
            if loan.transaction_amount < user_account.balance:
                user_account.balance -= loan.transaction_amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.loan_approve_status = True
                loan.transaction_type = 'Loan_Paid'
                loan.save()
                return redirect('transactions:loan_list')
            else:
                messages.error(self.request, f'Loan amount is greater than available balance')

        return redirect('loan_list')

class LoanListView(LoginRequiredMixin,ListView):
    model = Transaction
    template_name = 'transactions/loan_request.html'
    context_object_name = 'loans' # loan list ta ei loans context er moddhe thakbe
    
    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account=user_account,transaction_type='Loan Request')
        return queryset