"""Admin registrations for the example app.

The plugin owns its own admin surface — we just opt in via
``register_admin`` and register our source model alongside it.
"""

from django.contrib import admin
from django_pgai.contrib.admin import register_admin

from pgai_example.models import Movie

admin.site.register(Movie)
register_admin(admin.site)
