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
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('approve_tenant/<int:tenant_id>/', views.approve_tenant, name='approve_tenant'),
    path('reject_tenant/<int:tenant_id>/', views.reject_tenant, name='reject_tenant'),
    path('admin/', admin.site.urls),
    path('index/', views.index, name='index'),
    path('', views.new_login, name='login'),
    path('Registration/', views.Registration, name='Registration'),
    path('ApplicationStatus/', views.ApplicationStatus, name='ApplicationStatus'),
    path('signup_homeowner/', views.signup_homeowner, name='signup_homeowner'),
    path('SignUpPolice/', views.SignUpPolice, name='SignUpPolice'),
    path('HomeOwnerdashboard/', views.HomeOwnerdashboard, name='HomeOwnerdashboard'),
path('payment/', views.payment, name='payment'),
path('process_payment/', views.process_payment, name='process_payment'),
    path('Policedashboard/', views.Policedashboard, name='Policedashboard'),
    path('police/approve/<int:tenant_id>/', views.police_approve_tenant, name='police_approve_tenant'),
    path('police/reject/<int:tenant_id>/', views.police_reject_tenant, name='police_reject_tenant'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('check-verification/', views.check_verification, name='check_verification'),
    path('logout/', views.logout_view, name='logout'),
    path('payment/', views.payment, name='payment'),
    path('process-payment/', views.process_payment, name='process_payment'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
