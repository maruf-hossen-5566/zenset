import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Load environment variables
load_dotenv()


# Build paths inside the project like this: BASE_DIR / 'subdir'.


BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production

# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/


# SECURITY WARNING: keep the secret key used in production secret!

# SECRET_KEY = "django-insecure-k(a40#gbfa^-tf25(k1%_e5@no#p-@j$!b-o910ey6gzdm#her"
SECRET_KEY = os.getenv("SECRET_KEY")


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"


ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split(",")


# --- Security settings ---
if DEBUG:
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]
else:
    # Production security settings
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Add trusted origins for Railway
    CSRF_TRUSTED_ORIGINS = [
        "https://*.railway.app",
        "https://*.up.railway.app",
    ]


# --- Default User models

AUTH_USER_MODEL = "auth_app.CustomUser"


# Application definition


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    # "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "user_sessions",
    "django_user_agents",
    "blog_app",
    "auth_app",
    "profile_app",
    "me_app",
    "search_app",
    "like_app",
    "comment_app",
    "notification_app",
    "debug_toolbar",
    "test_app",
    "contact_app",
    "email_app",
    "suggestion_app",
    "cloudinary",
]


MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # "django.contrib.sessions.middleware.SessionMiddleware",
    "user_sessions.middleware.SessionMiddleware",  # Add this line
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
]


ROOT_URLCONF = "blog_project_with_flowbite.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "blog_project_with_flowbite.wsgi.application"


# --- DATABASE ---
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
if DEBUG:
    # --- SQLite ---
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    # --- Railway PostgreSQL ---
    DATABASES = {
        "default": dj_database_url.config(
            default=os.getenv("DATABASE_URL"),
            conn_max_age=600,
        )
    }

# --- CACHE CONFIGURATION ---
if DEBUG:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            # "LOCATION": os.getenv("LOCAL_REDIS_URL"),
            "LOCATION": os.getenv("RAILWAY_REDIS_URL"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "SOCKET_CONNECT_TIMEOUT": 5,  # in seconds
                "SOCKET_TIMEOUT": 5,  # in seconds
                "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
                "IGNORE_EXCEPTIONS": True,
                "DJANGO_REDIS_SCAN_ITERSIZE": 100_000,  # Add this line
            },
            "KEY_PREFIX": "blog_project_with_flowbite",  # Helps identify your project's keys in Redis
        }
    }
    CACHE_TTL = 60 * 15


# Password validation

# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization

# https://docs.djangoproject.com/en/5.1/topics/i18n/


LANGUAGE_CODE = "en-us"


# --- LOGIN CONF ---
# LOGIN_REDIRECT_URL = 'blog:index'
LOGIN_REDIRECT_URL = "blog:index"
LOGIN_URL = "auth:login"
LOGOUT_REDIRECT_URL = "blog:index"


# --- STATIC FILES ---
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# Add internal IPs
INTERNAL_IPS = [
    "127.0.0.1",
]


# --- EMAIL CONFIGURATION ---
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")  # Your Gmail address
EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD"
)  # The password you just generated
DEFAULT_FROM_EMAIL = f"Zenset <{os.getenv('EMAIL_HOST_USER')}>"

# --- USER AGENTS ---
USER_AGENTS_CACHE = "default"


# --- USER SESSION
SESSION_ENGINE = "user_sessions.backends.db"
SILENCED_SYSTEM_CHECKS = ["admin.E410"]
SESSION_CACHE_ALIAS = "default"
if DEBUG:
    # -- For production
    SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 days
    SESSION_COOKIE_SECURE = True  # Only send cookie over HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to session cookie
    SESSION_SAVE_EVERY_REQUEST = True  # Update session on every request

USE_TZ = True
TIME_ZONE = "Asia/Dhaka"  # Your local timezone


# --- CLOUDINARY CONFIGURATION ---
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
    "SECURE": True,
    "STATIC_TRANSFORMATIONS": {
        "image": {
            "quality": "auto",
            "fetch_format": "auto",
            "dpr": "auto",
        },
        "profile_pictures": {
            "quality": "auto:good",
            "fetch_format": "auto",
            "dpr": "auto",
            "responsive": True,
            "width": "auto",
            "crop": "fill",
        },
    },
}


# --- LOGGING ---
if DEBUG:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
            "file": {
                "level": "DEBUG",
                "class": "logging.FileHandler",
                "filename": os.path.join(BASE_DIR, "logs/debug.log"),
            },
        },
        "loggers": {
            "": {
                "handlers": ["console", "file"],
                "level": "DEBUG",
                "propagate": True,
            },
        },
    }
else:
    # Production logging - only console logging
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": "INFO",
            },
        },
    }
