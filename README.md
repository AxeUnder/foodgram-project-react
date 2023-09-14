# FoodGram
>[FoodGram](http://foodgram.zapto.org:8080/)

## Описание
«Фудграм» — это сайт, на котором можно публиковать собственные рецепты, добавлять чужие рецепты в избранное, подписываться на других авторов и создавать список покупок для заданных блюд.
Вот, что было сделано в ходе работы над проектом:
- настроено взаимодействие Python-приложения с внешними API-сервисами;
- создан собственный API-сервис на базе проекта Django;
- подключено SPA к бэкенду на Django через API;
- созданы образы и запущены контейнеры Docker;
- созданы, развёрнуты и запущены на сервере мультиконтейнерные приложения;
- закреплены на практике основы DevOps, включая CI&CD.

**Инструменты и стек:** #python #JSON #YAML #Django #React #Telegram #API #Docker #Nginx #PostgreSQL #Gunicorn #JWT #Postman

## Запуск приложения в контейнере на сервере
1. На сервере создайте директорию для приложения:
    ```bash
    mkdir foodgram/infra
    ```
2. В папку _infra_ скопируйте файлы `docker-compose.production.yml`, `nginx.production.conf`.
3. Там же создайте файл `.env` со следующими переменными:
   ```
   SECRET_KEY=... # секретный ключ django-проекта
   DEBUG=False
   ALLOWED_HOSTS=... # IP/домен хоста, БД (указывается через запятую без пробелов)
   DB_ENGINE=django.db.backends.postgresql # работаем с БД postgresql
   DB_NAME=db.postgres # имя БД
   POSTGRES_USER=... # имя пользователя БД
   POSTGRES_PASSWORD=... # пароль от БД
   DB_HOST=db
   DB_PORT=5432
   ```
4. В соответствии с `ALLOWED_HOSTS` измените `nginx.production.conf`.
5. Подключаем ssl сертификат для домена. Для это скачиваем certbot и получаем сертификат:
   ```bash
   sudo snap install --classic certbot
   sudo ln -s /snap/bin/certbot /usr/bin/certbot
   sudo certbot --nginx
   sudo certbot renew --dry-run
   ```
6. Теперь соберем и запустим контейнер:
   ```bash
   sudo docker compose up --build
   ```
7. В новом окне терминала создадим супер пользователя:
   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

## Инфраструктура проекта
**Главная** - https://localhost/recipes/ \
**API** - https://localhost/api/ \
**Redoc** - https://localhost/api/docs/ \
**Админка** -https://localhost/admin/

## Примеры запросов
1. Получение списка рецептов: \
   **GET** `/api/recipes/` \
   REQUEST
   ```json
   {
     "count": 123,
     "next": "http://127.0.0.1:8000/api/recipes/?page=2",
     "previous": "http://127.0.0.1:8000/api/recipes/?page=1",
     "results": [
       {
         "id": 0,
         "tags": [
           {
             "id": 0,
             "name": "Завтрак",
             "color": "green",
             "slug": "breakfast"
           }
         ],
         "author": {
           "email": "ya@ya.ru",
           "id": 0,
           "username": "user",
           "first_name": "Ivan",
           "last_name": "Zivan",
           "is_subscribed": false
         },
         "ingredients": [
           {
             "id": 0,
             "name": "Курица",
             "measurement_unit": "г",
             "amount": 100
           }
         ],
         "is_favorited": false,
         "is_in_shopping_cart": false,
         "name": "string",
         "image": "https://backend:8080/media/recipes/images/image.jpeg",
         "text": "string",
         "cooking_time": 10
       }
     ]
   }
   ```
2. Регистрация пользователя: \
   **POST** `/api/users/` \
   RESPONSE
   ```json
   {
     "email": "ya@ya.ru",
     "username": "user",
     "first_name": "Ivan",
     "last_name": "Zivan",
     "password": "super_password1"
   }
   ```
   REQUEST
   ```json
   {
   "email": "ya@ya.ru",
   "id": 0,
   "username": "user",
   "first_name": "Ivan",
   "last_name": "Zivan"
   }
   ```
3. Подписаться на пользователя: \
   **POST** `/api/users/{id}/subscribe/`
   REQUEST
   ```json
   {
     "email": "user@example.com",
     "id": 0,
     "username": "user",
     "first_name": "Ivan",
     "last_name": "Zivan",
     "is_subscribed": true,
     "recipes": [
       {
         "id": 0,
         "name": "string",
         "image": "https://backend:8080/media/recipes/images/image.jpeg",
         "cooking_time": 10
       }
     ],
     "recipes_count": 1
   }
   ```
## Об авторе
Python-разработчик **[AxeUnder](https://github.com/AxeUnder)**.