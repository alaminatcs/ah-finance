from django.urls import path
from .views import welcome_note, SignupView, UserLogin, UserLogout

app_name = 'accounts'
urlpatterns = [
    path('', welcome_note, name='home'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
]