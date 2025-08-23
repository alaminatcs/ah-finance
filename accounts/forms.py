from .models import User, UserBankAccount, UserAddress, ACCOUNT_TYPE, GENDER_TYPE
from django.contrib.auth.forms import UserCreationForm
from django import forms

class UserRegistrationForm(UserCreationForm):
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    birth_date = forms.CharField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    street_address = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    city = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100)
    
    class Meta:
        model = User
        fields = [
            'account_type', 'username', 'first_name', 'last_name', 'birth_date', 'gender', 'email',
            'street_address', 'postal_code', 'city', 'country', 'password1', 'password2'
        ]
    
    def save(self, commit=True):            #customize for save 3 models data together 
        new_user = super().save(commit=False)
        
        if commit == True:
            new_user.save()

            account_type = self.cleaned_data['account_type']
            birth_date = self.cleaned_data['birth_date']
            gender = self.cleaned_data['gender']
            UserBankAccount.objects.create(
                user = new_user,
                birth_date = birth_date,
                gender = gender,
                account_type = account_type,
                account_no = new_user.id + (100000 if account_type=='Savings' else 200000)
            )

            street_address = self.cleaned_data['street_address']
            postal_code = self.cleaned_data['postal_code']
            city = self.cleaned_data['city']
            country = self.cleaned_data['country']
            UserAddress.objects.create(
                user = new_user,
                street_address = street_address,
                postal_code = postal_code,
                city = city,
                country = country
            )
        return new_user