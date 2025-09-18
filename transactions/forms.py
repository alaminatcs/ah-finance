from django import forms
from .models import Transaction

# parent class of each type of transaction form
class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'transaction_amount']

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        if self.account is None:
            raise ValueError("Required an account for TransactionForm")

        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True
        # self.fields['transaction_type'].widget = forms.HiddenInput()
        self.fields['transaction_type'].widget.attrs = {'style': 'opacity:0.2;'}

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save(commit=commit)

# deposit form
class DepositForm(TransactionForm):
    def clean_transaction_amount(self):
        amount = self.cleaned_data['transaction_amount']
        if amount < 500:
            raise forms.ValidationError('You need to deposit at least $500')
        return amount

# withdraw form
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

# loan request form
class LoanRequestForm(TransactionForm):
    def clean_transaction_amount(self):
        amount = self.cleaned_data['transaction_amount']
        if amount < 50000:
            raise forms.ValidationError('You can request for loan at least $50000')
        if amount > 500000:
            raise forms.ValidationError('You can request for loan at most $500000')
        return amount