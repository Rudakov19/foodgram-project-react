from django.contrib import admin

from users.models import User, Subscribe

admin.site.register(User)
admin.site.register(Subscribe)
