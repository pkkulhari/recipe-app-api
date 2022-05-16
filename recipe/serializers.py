from rest_framework import serializers

from recipe.models import Ingredient, Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")
        read_only_fields = ("id",)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name")
        read_only_fields = ("id",)


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    ingredients = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = ("id", "title", "time_minutes", "price", "link", "tags", "ingredients")
        read_only_fields = ("id",)


class RecipeDetailSerializer(RecipeSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
