from django.urls import path
from .views import welcome_note, UserSignup, UserLogin, UserLogout, ProfileDetails, UserDataUpdate

app_name = 'accounts'
urlpatterns = [
    path('', welcome_note, name='home'),
    path('signup/', UserSignup.as_view(), name='signup'),
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('profile/', ProfileDetails.as_view(), name='profile'),
    path('profile-edit/', UserDataUpdate.as_view(), name='update')
]