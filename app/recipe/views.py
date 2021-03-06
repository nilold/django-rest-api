from core.models import Tag, Ingredient, Recipe, RecipeBook
from recipe import serializers
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class BasicRecipeViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin
):
    """Basic models view set"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        assigned_only = bool(int(self.request.query_params.get("assigned_only", 0)))

        queryset = self.queryset

        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(user=self.request.user).order_by("-name").distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(BasicRecipeViewSet):
    """Manage tags in the database"""

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BasicRecipeViewSet):
    """Manage ingredients in the database"""

    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeBookViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RecipeBookSerializer
    queryset = RecipeBook.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.RecipeBookDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-id")


def _params_to_ints(qs):
    """Converts a list of string ids to a list of integers"""
    return [int(str_id) for str_id in qs.split(",")]


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in the database"""

    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")

        queryset = self.queryset

        if tags:
            tag_ids = _params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredients_ids = _params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_ids)

        return queryset.filter(user=self.request.user).order_by("-id")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.RecipeDetailSerializer
        elif self.action == "upload_image":
            return serializers.RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload a image to a recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
