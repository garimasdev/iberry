"""
Django settings for core project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
from pathlib import Path

# phonepe payment gateway
from phonepe.sdk.pg.env import Env



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'dsfadsgdagdsgadgadgad'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # apps
    'accounts',
    'dashboard',
    'stores',
    'notification',
    
    #other apps
    'rest_framework',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'push_notifications',
    'sslserver',
    'django_filters',
    'import_export',
    'pwa',

    
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

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'stores.context_processors.cart_count',
                'stores.context_processors.notification_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

#Auth Settings
AUTH_USER_MODEL = 'accounts.User'
# AUTHENTICATION_BACKENDS = ['accounts.backends.EmailBackend']

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'iberry',
        'USER': 'root',
        # 'PASSWORD': 'password123',
        # 'PASSWORD': 'password',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306'
    }
}


###### Api 
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
}



########## SMS Settings
SMS_USERNAME = 'iberrtrpg.trans';
SMS_PASSWORD = 'atwFc';
SMS_FROM = 'IBWIFI';
SMS_DLT_PRINCIPAL_ID = '1301160933730426574';
SMS_DLT_CONTENT_ID = '1307168136868522350';
SMS_TEMPLATE = 'Click #LINK# to access hotel Phone System and Food menu. #TOKEN#Welcome to ibudha.com';






# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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

# push notification
PUSH_NOTIFICATIONS_SETTINGS = {
    "FCM_API_KEY": "AAAAoRElnP4:APA91bHYM9GD4Z-QA0dOR2mb9SYVKaK1ffaMjChzhzNXeu1feYiikUMegPsGb9_p5Rt7ZCxMDqmYWICBa6ix_DweSqnrI532agCW7PQzMUFIwK5624vOqmMS0opNnscaGPMbMnmNuOy8",
    # "GCM_API_KEY": "[your api key]",
    # "APNS_CERTIFICATE": "/path/to/your/certificate.pem",
    # "APNS_TOPIC": "com.example.push_test",
    # "WNS_PACKAGE_SECURITY_ID": "[your package security id, e.g: 'ms-app://e-3-4-6234...']",
    # "WNS_SECRET_KEY": "[your app secret key, e.g.: 'KDiejnLKDUWodsjmewuSZkk']",
    "WP_PRIVATE_KEY": os.path.join(BASE_DIR, "private_key.pem"),
    "WP_CLAIMS": {'sub': "mailto:sammrafi9@gmail.com"},
    "UPDATE_ON_DUPLICATE_REG_ID": True,
}

TELEGRAM = {
    "bot_token": "6954115938:AAHSdZOJaCFz4qduUE3ppMBB7mHUVfYg8q8"
    # "bot_token": "6071425680:AAGWmXo37l0FdD415w8zxXdghbm_E8IvN44"
}

# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

if DEBUG:
  STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
else:
  STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/')

# Login setup
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CSRF_COOKIE_SECURE = True  # Set to True if your site is served over HTTPS
CSRF_COOKIE_HTTPONLY = True  # This prevents JavaScript from accessing the CSRF cookie
CSRF_COOKIE_SAMESITE = 'Lax'  # Adjust as needed ('Lax', 'Strict', 'None')

CSRF_TRUSTED_ORIGINS = ['https://iberry.caucasianbarrels.com', 'https://iberry.caucasianbarrels.com']


RAZORPAY_CLIENT_ID= 'rzp_test_8ZwgsznY2VAfPP'
RAZORPAY_CLIENT_SECRET= 'MOFA1TdFPjB9uPNztJrXnacB'


# Phonepe payment uat creds
# MERCHANT_ID= "JULLUNDURUAT"  
# SALT_KEY= "b0954cf9-927d-4292-9de9-94c3a6b73890" 
# SALT_INDEX= 1 
# ENV= Env.UAT


# Phonepe payment prod creds
MERCHANT_ID= "M22LCRP3AUE3O"  
SALT_KEY= "acff9b57-fe8b-42dc-bc46-9e5e0113a4be" 
SALT_INDEX= 1 
ENV= Env.PROD


# pwa service worker
# PWA_SERVICE_WORKER_PATH = os.path.join(BASE_DIR, 'static/js', 'serviceworker.js')


# # pwa manifest.json 
# PWA_APP_NAME = 'Iberry'
# PWA_APP_DESCRIPTION = "Iberry PWA"
# PWA_APP_THEME_COLOR = '#4154f1'
# PWA_APP_BACKGROUND_COLOR = '#f6f9ff'
# PWA_APP_DISPLAY = 'standalone'
# PWA_APP_SCOPE = '/'
# PWA_APP_ORIENTATION = 'any'
# # PWA_APP_START_URL = '/'
# PWA_APP_START_URL = '/store/97599568/foods/outdoor_items/'
# PWA_APP_STATUS_BAR_COLOR = 'default'
# PWA_APP_ICONS = [
# 	{
# 		'src': 'static/images/iberry_logo.png',
# 		# 'sizes': '160x160'
#         'sizes': '320x320'
# 	}
# ]
# PWA_APP_ICONS_APPLE = [
# 	{
# 		'src': 'static/images/iberry_logo.png',
# 		'sizes': '320x320'
# 	}
# ]
# PWA_APP_SPLASH_SCREEN = [
# 	{
# 		'src': 'static/images/icon.png',
# 		'media': '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)'
# 	}
# ]
# PWA_APP_DIR = 'ltr'
# PWA_APP_LANG = 'en-US'
