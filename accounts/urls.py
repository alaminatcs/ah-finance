from django.urls import path
from .views import welcome_note, UserSignup, UserLogin, UserLogout, UserDataUpdate, update_view

app_name = 'accounts'
urlpatterns = [
    path('', welcome_note, name='home'),
    path('signup/', UserSignup.as_view(), name='signup'),
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('profile-update', UserDataUpdate.as_view(), name='update'),
    # path('profile-update', update_view, name='update'),
]