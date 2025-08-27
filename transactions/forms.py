from django import forms
from .models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_amount', 'transaction_type']

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        if self.account is None:
            raise ValueError("TransactionForm requires 'account' kwarg")

        super().__init__(*args, **kwargs)
        # self.fields['transaction_type'].disabled = True
        self.fields['transaction_type'].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save(commit=commit)

class DepositForm(TransactionForm):
    def clean_transaction_amount(self):
        amount = self.cleaned_data['transaction_amount']
        if amount < 500:
            raise forms.ValidationError('You need to deposit at least $500')
        return amount

class WithdrawForm(TransactionForm):
    def clean_transaction_amount(self):
        amount = self.cleaned_data['transaction_amount']
        if amount < 500:
            raise forms.ValidationError('You can withdraw at least $500')
        if amount > 50000:
            raise forms.ValidationError('You can withdraw at most $50000')
        if amount > self.account.balance:
            raise forms.ValidationError("You don't have sufficient balance")
        return amount

class LoanRequestForm(TransactionForm):
    def clean_transaction_amount(self):
        amount = self.cleaned_data['transaction_amount']
        if amount > 500000:
            raise forms.ValidationError('You can request loan at most $500000')
        return amount