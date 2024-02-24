from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User


MIN_MEANING = 1  # Минимальное значение для валидации
MAX_MEANING = 32000  # Максимальное значение для валидации


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True
    )
    color = models.CharField(
        'Цвет в HEX',
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=200,
        unique=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'Наименование ингредиента',
        max_length=200,
        unique=True
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=7,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Список ингредиентов',
        through='Recipe_ingredient'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список id тегов'
    )
    image = models.ImageField(
        'Картинка, закодированная в Base64',
        upload_to='recipes/',
        blank=True
    )
    name = models.CharField(
        'Название',
        max_length=200,
    )
    text = models.TextField(
        'Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            MinValueValidator(MIN_MEANING),
            MaxValueValidator(MAX_MEANING)
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Recipe_ingredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество в рецепте',
        validators=[
            MinValueValidator(MIN_MEANING),
            MaxValueValidator(MAX_MEANING)
        ]
    )

    class Meta:
        verbose_name = 'Рецепт из ингредиентов'
        verbose_name_plural = 'Рецепты из ингредиентов'

    def __str__(self):
        return f'{self.ingredient.name} в {self.recipe.name}'


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт',
        related_name='favorite_recipe'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Добавил в избранное',
        related_name='favorite_user'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'{self.user.username} добавил в избранное {self.recipe.name}'


class Shopping_cart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт в покупках'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Добавил в покупку'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'{self.user.username} добавил в покупки {self.recipe.name}'
