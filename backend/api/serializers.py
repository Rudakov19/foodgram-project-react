from django.db import transaction

from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Tag, Ingredient, Recipe, RecipeIngredient,
                            MIN_MEANING, MAX_MEANING)
from users.models import User


class UserSerializer(UserSerializer):
    """Профиль пользователя."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, author):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return author.authors.filter(user=request.user).exists()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class UserCreateSerializer(UserCreateSerializer):
    """Регистрация пользователя."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Для рецептов."""

    name = serializers.ReadOnlyField()
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Мои подписки."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, author):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return author.authors.filter(user=request.user).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context['request']
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSerializer(recipes, read_only=True, many=True)
        return serializer.data

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )


class TagSerializer(serializers.ModelSerializer):
    """Список тегов."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Список ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов в рецепт."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        max_value=MAX_MEANING, min_value=MIN_MEANING
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Количество ингредиентов для рецепта."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Просмотр списка рецептов."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(read_only=True, many=True,
                                             source='recipeingredient')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    def get_is_favorited(self, recipe):
        request = self.context['request']
        if not request.user.is_authenticated:
            return False
        return recipe.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context['request']
        if not request.user.is_authenticated:
            return False
        return recipe.shoppingcarts.filter(user=request.user).exists()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'image', 'name', 'text', 'cooking_time')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Создание рецепта."""

    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientWriteSerializer(
        many=True
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        max_value=MAX_MEANING, min_value=MIN_MEANING
    )

    def validate(self, obj):
        if Recipe.objects.filter(name=obj['name']).exists():
            raise serializers.ValidationError(
                'Такой рецепт уже есть!')
        return obj

    @transaction.atomic
    def create_ingredient(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        request = self.context['request']
        recipe = Recipe.objects.create(author=request.user,
                                       **validated_data)
        recipe.tags.set(tags)
        self.create_ingredient(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.recipeingredient.all().delete()
        self.create_ingredient(instance, ingredients)
        instance.tags.set(tags)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'tags',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time'
        )
