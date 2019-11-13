from rest_framework import serializers
from core.models import Tag, Ingredient, Recipe, RecipeBook


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
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ("id", "title", "ingredients", "tags", "time_minutes", "price", "link")
        read_only_fields = ("id",)


class RecipeDetailSerializer(RecipeSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uplaoding images to recipes"""

    class Meta:
        model = Recipe
        fields = ("id", "image")
        read_only_fields = ("id",)


class RecipeBookSerializer(serializers.ModelSerializer):
    recipes = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Recipe.objects.all()
    )

    class Meta:
        model = RecipeBook
        fields = ("id", "title", "recipes")
        read_only_fields = ("id",)


class RecipeBookDetailSerializer(RecipeBookSerializer):
    recipes = RecipeDetailSerializer(many=True, read_only=True)
