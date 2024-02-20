from django.contrib import admin
from recipes.models import Ingredient, Tag

# Register Ingredient model
admin.site.register(Ingredient)

# Register Tag model
admin.site.register(Tag)
