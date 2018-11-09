from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView

from twauth.views import home

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('auth/', include('social_django.urls', namespace='social')),
    path('', home, name='home'),
]
