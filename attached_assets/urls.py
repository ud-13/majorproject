"""
URL configuration for Tenant project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Tenant import views
from django.views.generic import TemplateView
from.views import login, send_otp, verify_otp
from .views import Registration 



urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index, name='index'),
    path('', views.login, name='login'),
    path('Registration/', views.Registration, name='Registration'),
    #path('Payment/', views.Payment, name='Payment'),
    path('ApplicationStatus/', views.ApplicationStatus, name='ApplicationStatus'),
    path('signup_Homeowner/', views.signup_homeowner, name='signup_Homeowner'),
    path('SignUpPolice/', views.SignUpPolice, name='SignUpPolice'),
    path('HomeOwnerdashboard/', views.HomeOwnerdashboard, name='HomeOwnerdashboard'),
    path('Policedashboard/', views.Policedashboard, name='Policedashboard'),


    #path('Policedashboard/', views.Policedashboard, name='Policedashboard'),
    #path('police/approve/<int:tenant_id>/', views.police_approve_tenant, name='police_approve_tenant'),
    #path('police/reject/<int:tenant_id>/', views.police_reject_tenant, name='police_reject_tenant'),

  
    #path('lo/', login, name='login'),
    path('send-otp/', send_otp, name='send_otp'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('check-verification/', views.check_verification, name='check_verification'),
]


   
   
    
    
