# Foodrgam
Проект «Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.
#### Технологии
 - Python 3.9
 - Django 3.2.3
 - Django REST framework 3.12.4
 - Nginx
 - Gunicorn
 - Docker
 - Postgres

##### Локальное развертывание проекта
1. Клонируйте репозиторий [foodgram-project-react](https://github.com/Rudakov19/foodgram-project-react).
2. В каталоге с проектом создайте и активируйте виртуальное окружение: `python3 -m venv venv && source venv/bin/activate`
3. Установите зависимости: `pip install -r requirements.txt`.
4. Выполните миграции: `python manage.py migrate`.
5. Создайте суперюзера: `python manage.py createsuperuser`.
6. В файле settings.py список ALLOWED_HOSTS должен выглядеть так:  `ALLOWED_HOSTS = ['your_ip', '127.0.0.1', 'localhost', 'your_domain']`.

##### Создание Docker-образов
1. Замените username на ваш логин на DockerHub:
```
cd frontend
docker build -t username/foodgram_frontend .
cd ../backend
docker build -t username/foodgram_backend .
cd ../nginx
docker build -t username/foodgram_gateway .
```
2. Загрузите образы на DockerHub:
```
docker push username/foodgram_frontend
docker push username/foodgram_backend
docker push username/foodgram_gateway
```

##### Установка проекта на сервер

1. Подключитесь к удаленному серверу

```ssh -i путь_до_файла_с_SSH_ключом/название_файла_с_SSH_ключом имя_пользователя@ip_адрес_сервера ```

2. Создайте на сервере директорию foodgram

`mkdir foodgram`

3. Установка docker compose на сервер:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```

В kittygram скопируйте файлы docker-compose.production.yml и .env:
```
scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/kittygram/docker-compose.production.yml
```

4. Запустите docker compose в режиме демона:

`sudo docker compose -f docker-compose.production.yml up -d`

5. Выполните миграции, соберите статику бэкенда и скопируйте их в /backend_static/static/:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

6. На сервере в редакторе nano откройте конфиг Nginx:

`sudo nano /etc/nginx/sites-enabled/default`

7. Добавте настройки location в секции server:
```
location / {
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:8000;
}
```

8. Проверьте работоспособность конфигураций и перезапустите Nginx:
```
sudo nginx -t
sudo service nginx reload
```
##### Переменные окружения
В корневом каталоге проекта создайте файл .env:
```
SECRET_KEY = '<ваш_ключ>'
DEBUG = False
ALLOWED_HOSTS = 'ваш домен'
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
DB_HOST=db
DB_PORT=5432
```

#### Примеры запросов и ответов:
#### Запрос:

| Ресурс | Тип | Путь |
| ------ | ------ | ------ |
| Текущий пользователь | GET | /api/users/me/ |
#### Ответ:
```
{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "is_subscribed": false
}
```
#### Запрос:

| Ресурс | Тип | Путь |
| ------ | ------ | ------ |
| Текущий пользователь | GET | /api/recipes/0/ |
#### Ответ:
```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    }
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```
### Автор:
[Дмитрий Рудаков](https://github.com/Rudakov19)
