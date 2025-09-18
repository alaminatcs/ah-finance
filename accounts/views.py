from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.forms import UserRegistrationForm, UserDataUpdateForm
from django.views.generic import TemplateView, View, FormView, DetailView, UpdateView

# home view
class HomeView(TemplateView):
    template_name = 'base.html'

# signup view
class UserSignup(FormView):
    form_class = UserRegistrationForm
    template_name = 'accounts/registration.html'
    success_url = reverse_lazy('accounts:home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'Create'
        return context

# login view
class UserLogin(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        return reverse_lazy('accounts:home')

# logout view
class UserLogout(LoginRequiredMixin, View):    
    def get(self, request):
        logout(request)
        return redirect('accounts:login')

# profile details view
class ProfileDetails(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # add related models to context
        context['account'] = getattr(self.object, 'account', None)
        context['address'] = getattr(self.object, 'address', None)
        return context

# profile update view
class UserDataUpdate(LoginRequiredMixin, UpdateView):
    form_class = UserDataUpdateForm
    template_name = 'accounts/registration.html'
    success_url = reverse_lazy('accounts:home')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'Update'
        return context