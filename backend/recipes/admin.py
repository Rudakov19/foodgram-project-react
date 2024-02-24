from django.contrib import admin

from recipes.models import (Ingredient, Tag, Recipe,
                            Recipe_ingredient, Favorite, Shopping_cart)


admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(Recipe_ingredient)
admin.site.register(Favorite)
admin.site.register(Shopping_cart)
