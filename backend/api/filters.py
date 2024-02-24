from django_filters.rest_framework import FilterSet, filters
from recipes.models import Tag, Recipe


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(),
                                             field_name='tags__slug',
                                             to_field_name='slug',
                                             )
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter')
    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter')

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if not (value and user.is_authenticated):
            return queryset
        return queryset.filter(favorite_recipe__user=user)

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if not (value and user.is_authenticated):
            return queryset
        return queryset.filter(shopping_recipe__user=user)
