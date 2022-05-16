from django.contrib import admin

from recipe.models import Ingredient, Recipe, Tag

admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
