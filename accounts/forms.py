from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserBankAccount, UserAddress, ACCOUNT_TYPE, GENDER_TYPE

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
    
    def save(self, commit=True):            #save 3 models data together 
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
                account_no = new_user.id + 100000
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

class UserDataUpdateForm(forms.ModelForm):
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    street_address = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    city = forms.CharField(max_length=100)
    country = forms.CharField(max_length=100)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance:
            user_account = UserBankAccount.objects.get(user=self.instance)
            # user account instance
            if user_account:
                self.fields['account_type'].initial = user_account.account_type
            
            user_address = UserAddress.objects.get(user=self.instance)
            if user_address:
                    self.fields['street_address'].initial = user_address.street_address
                    self.fields['city'].initial = user_address.city
                    self.fields['postal_code'].initial = user_address.postal_code
                    self.fields['country'].initial = user_address.country

    def save(self, commit=True):
        cur_user = super().save(commit=False)

        if commit == True:
            cur_user.save()
            # update or create UserBankAccount
            user_account, created = UserBankAccount.objects.get_or_create(user=cur_user)
            user_account.account_type = self.cleaned_data['account_type']
            user_account.save()
            
            user_address, created = UserAddress.objects.get_or_create(user=cur_user)
            user_address.street_address = self.cleaned_data['street_address']
            user_address.postal_code = self.cleaned_data['postal_code']
            user_address.city = self.cleaned_data['city']
            user_address.country = self.cleaned_data['country']
            user_address.save()
        return cur_user