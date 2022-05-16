from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe.views import IngredientViewSet, ReciepViewSet, TagViewSet

router = DefaultRouter()
router.register("tags", TagViewSet)
router.register("ingredients", IngredientViewSet)
router.register("recipes", ReciepViewSet)

app_name = "recipe"
urlpatterns = [
    path("", include(router.urls)),
]
