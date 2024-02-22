from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from api.views import (RecipeViewSet, IngredientViewSet,
                       TagViewSet, UserViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    # Создание и удаление токена.
    url(r'^', include(router_v1.urls)),  # Работа с пользователями
    url(r'^auth/', include('djoser.urls.authtoken')),  # Работа с токенами
]
