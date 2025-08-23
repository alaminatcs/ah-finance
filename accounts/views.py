from django.shortcuts import render, redirect
from django.views.generic import View, FormView
from accounts.forms import UserRegistrationForm
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView


# Create your views here.
def welcome_note(request):
    return render(request, 'base.html')


class SignupView(FormView):
    form_class = UserRegistrationForm
    template_name = 'accounts/registration.html'
    success_url = reverse_lazy('accounts:home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class UserLogin(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        return reverse_lazy('accounts:home')


class UserLogout(View):    
    def get(self, request):
        logout(request)
        return redirect('accounts:login')