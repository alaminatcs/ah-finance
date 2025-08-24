from django.shortcuts import render, redirect
from django.views.generic import View, FormView, DetailView, UpdateView
from accounts.forms import UserRegistrationForm, UserDataUpdateForm
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
def welcome_note(request):
    return render(request, 'base.html')

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

class UserLogin(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        return reverse_lazy('accounts:home')

class UserLogout(View):    
    def get(self, request):
        logout(request)
        return redirect('accounts:login')

def update_view(request):
    if request.method == 'POST':
        form = UserDataUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('accounts:home')
    else:
        form = UserDataUpdateForm(instance=request.user)
    return render(request, 'accounts/registration.html', {'type': 'Update', 'form': form})

# class UserDataUpdate(FormView):
#     template_name = 'accounts/registration.html'
#     form_class = UserDataUpdateForm
#     success_url = reverse_lazy('accounts:home')

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['instance'] = self.request.user
#         return kwargs

#     def form_valid(self, form):
#         form.save()
#         return super().form_valid(form)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['type'] = 'Update'
#         return context

class UserDataUpdate(UpdateView):
    form_class = UserDataUpdateForm
    template_name = 'accounts/registration.html'
    success_url = reverse_lazy('accounts:home')

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['type'] = 'Update'
        return context