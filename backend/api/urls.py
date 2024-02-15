from django.conf.urls import url
from django.urls import include
from rest_framework import routers

router_v1 = routers.DefaultRouter()

urlpatterns = [
    # Создание и удаление токена.
    url(r'^auth/', include('djoser.urls')),  # Работа с пользователями
    url(r'^auth/', include('djoser.urls.authtoken')),  # Работа с токенами
]
