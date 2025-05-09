"""
Django settings for Tenant project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4auw7d-1gmfzlnq!^)=x1s$=@f@l*8sm_ck$84(o0(uf15k@+p'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', '89d0861d-aeb1-4734-8173-9926790c7772-00-3oxn964nzv0gc.riker.replit.dev', '*']

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = ['https://89d0861d-aeb1-4734-8173-9926790c7772-00-3oxn964nzv0gc.riker.replit.dev', 'https://*.replit.dev', 'https://*.repl.co']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Tenant',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Tenant.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':[
            os.path.join(BASE_DIR, 'Template'),
            os.path.join(BASE_DIR, 'attached_assets')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Tenant.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

STATICFILES_DIRS = [
    BASE_DIR / 'static' 
]

AUTH_USER_MODEL = 'Tenant.User' 

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # For Gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'pratapuday1176@gmail.com')  # Your Gmail
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'ejslkfwlznanyvhu')  # Generate in Google Account Security
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'pratapuday1176@gmail.com')  # Same as EMAIL_HOST_USER

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Create media directories if they don't exist
os.makedirs(os.path.join(MEDIA_ROOT, 'tenant_photos'), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, 'certificates'), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, 'signatures'), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, 'homeowner_photos'), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, 'aadhar_cards'), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, 'sikkim_certificates'), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, 'residential_certificates'), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT, 'land_parchas'), exist_ok=True)

FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# Session settings
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
