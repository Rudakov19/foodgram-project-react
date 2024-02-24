from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.pagination import CustomPagination
from api.permissions import AuthorOrReadOnly
from api.serializers import (UserSerializer, UserCreateSerializer,
                             SubscriptionsSerializer, IngredientSerializer,
                             TagSerializer, RecipeReadSerializer,
                             RecipeCreateSerializer, RecipeSerializer,
                             SubscribeAuthorSerializer)
from recipes.models import (Ingredient, Tag, Recipe, Recipe_ingredient)
from users.models import User, Subscribe


class UserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer
        return UserCreateSerializer

    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated,),
            pagination_class=CustomPagination)
    def subscriptions(self, request):
        context = {'request': request}
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(pages, many=True,
                                             context=context)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated,),)
    def subscribe(self, request, id):
        context = {'request': request}
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.metod == 'POST':
            serializer = SubscribeAuthorSerializer(author, data=request.data,
                                                 context=context)
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATE)

        if request.method == 'DELETE':
            get_object_or_404(Subscribe, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name', )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly, )
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated, ),
            pagination_class=CustomPagination)
    def favorite(self, request, id):
        context = {'request': request}
        user = request.user
        data = request.data
        recipe = get_object_or_404(Recipe, id=id)

        if request.method == 'POST':
            serializer = RecipeSerializer(recipe, data=data, context=context)
            serializer.is_valid(raise_exception=True)
            if not user.favorite_user.filter(recipe=recipe).exists():
                user.favorite_user.create(recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            favorite = get_object_or_404(user.favorite_user, recipe=recipe)
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(permissions.IsAuthenticated, ),)
    def shopping_cart(self, request, id):
        context = {'request': request}
        user = request.user
        data = request.data
        recipe = get_object_or_404(Recipe, id=id)

        if request.method == 'POST':
            serializer = RecipeSerializer(recipe, data=data, context=context)
            serializer.is_valid(raise_exception=True)
            if not user.shopping_user.filter(recipe=recipe).exists():
                user.shopping_user.create(recipe=recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            shoppingcart = get_object_or_404(user.shopping_user, recipe=recipe)
            shoppingcart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(permissions.IsAuthenticated, ),)
    def download_shopping_cart(self, request):
        ingredients_sum = (
            Recipe_ingredient.objects
            .filter(recipe__shopping_recipe__user=request.user)
            .order_by('ingredient__name')
            .annotate(total_amount=Sum('amount'))
            .values_list('ingredient__name', 'total_amount',
                         'ingredient__measurement_unit')
        )
        shopping_list = []
        [shopping_list.append(
            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients_sum]
        response = HttpResponse('Cписок покупок:\n' + '\n'.join(shopping_list),
                            content_type='text/plain')
        response['Content-Disposition'] = ('attachment; filename=shopping_list.txt')
        return response
