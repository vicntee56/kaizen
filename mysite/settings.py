import os
from pathlib import Path

# --- Ajustes para Render ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-vzm0nlqj6wd$hb9+*l4*wqjv(3q4!1#aiqrwnlxco5ec6h@k-=')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = [os.environ.get('RENDER_EXTERNAL_HOSTNAME', ''), 'localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']
# ---------------------------

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# SECURITY WARNING: keep the secret key used in production secret!


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'background_task',
    'myapp',  # Asegúrate de que sea solo 'myapp' y no 'myappmyapp'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 👈 agregado para Render
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Asegúrate de que esta línea esté presente
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'myapp.middleware.VerificacionMiddleware',  # ← aquí ya está bien con myapp
    'myapp.middleware.RegistrarVisitasMiddleware',  # al final de la lista
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Carpeta global de templates
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
WSGI_APPLICATION = 'mysite.wsgi.application'


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

TIME_ZONE = 'America/Santiago'  # Para Chile (ajusta según tu país)

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'

# Directorio donde se almacenan los archivos estáticos adicionales
STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Esto incluye la carpeta 'static' dentro de tu directorio de proyecto
]

STATIC_ROOT = BASE_DIR / 'staticfiles'  # Carpeta donde se copiarán los archivos estáticos compilados
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'  # 👈 agregado para Render

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = 'bcaceres.777@gmail.com'
EMAIL_HOST_PASSWORD = 'hwfc wixu gxds gnnf'  # Contraseña de aplicación válida


DEFAULT_FROM_EMAIL = EMAIL_HOST_USER


DEFAULT_FROM_EMAIL = EMAIL_HOST_USER  # El remitente por defecto

LOGIN_URL = '/signin/'  # La URL de tu vista de inicio de sesión

# Asegúrate de que CSRF_COOKIE_AGE esté configurado para permitir tiempo suficiente
CSRF_COOKIE_AGE = 31449600  # Esto da un año de duración al token CSRF


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


TRANSBANK_COMMERCE_CODE = '597055555532'
TRANSBANK_API_KEY = 'xnnnnnnnnnnnnnn'
TRANSBANK_RETURN_URL = 'http://127.0.0.1:8000/retorno/'  # Ajusta según tu entorno

GEOIP_PATH = os.path.join(BASE_DIR, 'GeoLite2-City.mmdb')
