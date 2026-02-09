"""
Application definition - installed apps configuration
"""

LIBRARY_APPS = [
    "django_pgai",
]

PROJECT_APPS = [
    "wiki_new",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
] + LIBRARY_APPS + PROJECT_APPS
