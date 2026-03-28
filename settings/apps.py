"""
Application definition - installed apps configuration
"""

LIBRARY_APPS = [
    "django_typer",
    "django_pgai",
]

PROJECT_APPS = [
    "pgai_example",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
# PROJECT_APPS placed before LIBRARY_APPS so that overrides in
# pgai_example/management/commands/ take precedence over django_pgai's
# (Django picks the first app in INSTALLED_APPS that provides a command).
] + PROJECT_APPS + LIBRARY_APPS
