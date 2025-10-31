import os
import environ
import re

from pathlib import Path
from logging import Filter

BASE_DIR = Path(__file__).resolve().parent.parent
REDACT_RE = re.compile(r'("?(email|address|name)"?\s*[:=]\s*")[^"]+(")', re.I)
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-insecure-key-change-me")
DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env("ALLOWED_HOSTS", default="127.0.0.1,localhost").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_filters",
    # Third-party
    "corsheaders",
    "axes",
    # local apps
    "core",
    "users",
    "profiles.apps.ProfilesConfig",
    "catalog",
    "bookings",
    "payments",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

ROOT_URLCONF = "core.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.exposure_banner",  # <-- added
            ],
        },
    }
]
WSGI_APPLICATION = "core.wsgi.application"

if os.environ.get("DB_NAME"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PASSWORD"),
            "HOST": env("DB_HOST", default="127.0.0.1"),
            "PORT": env("DB_PORT", default="5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3"
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

class PiiRedactor(Filter):
    def filter(self, record):
        msg = str(record.getMessage())
        record.msg = REDACT_RE.sub(r'\1[REDACTED]\3', msg)
        return True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "pii": {"()": PiiRedactor},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "filters": ["pii"],
            "level": "INFO",
        },
    },
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "project": {"handlers": ["console"], "level": "INFO"},
    },
}

# ---- Configurations ---- #
LANGUAGE_CODE = "en-us"
USE_TZ = True
TIME_ZONE = "Australia/Adelaide"
USE_I18N = True

# ---- Static Dir ---- #
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
_static_dir = BASE_DIR / "static"
STATICFILES_DIRS = [_static_dir] if _static_dir.exists() else []
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---- Login ---- #
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"
LOGIN_URL = "users:login"

# ---- Secure cookies / headers ---- #
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_HTTPONLY = True
SECURE_HSTS_SECONDS = 31536000     # set only in prod behind HTTPS
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "DENY"

# ---- Axes configuration ---- #
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_LOCKOUT_CALLABLE = None
AXES_RESET_ON_SUCCESS = True
AXES_LOCKOUT_TEMPLATE = "users/locked_out.html"
AXES_COOLOFF_TIME = 1              # hour
# whitelist your admin user:
AXES_USERNAME_CALLABLE = "core.utils.axes_get_username"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

PRIVACY_RETENTION_DAYS = int(env("PRIVACY_RETENTION_DAYS", default=15))