from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('contact/', views.contact_view, name='contact'),
    path('login-selection/', views.login_selection_view, name='login_selection'),
    path('login/', views.login_view, name='login'),
    path('signup-selection/', views.signup_selection_view, name='signup_selection'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('terms/', views.terms_view, name='terms'),
    path('about/', views.about_view, name='about'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password-phone/', views.reset_password_phone_view, name='reset_password_phone'),
]
