from django.urls import path

from . import views

urlpatterns = [
    # Главная страница
    path("", views.index, name="index"),
    # Посты группы
    path("group/<slug:slug>/", views.group_posts, name="group"),
    # Добавление новой записи
    path('new/', views.new_post, name='new_post'),
    # Профайл пользователя
    path('<str:username>/', views.profile, name='profile'),
    # Просмотр записи
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    # Редактирование записи
    path('<str:username>/<int:post_id>/edit/', views.post_edit,
         name='post_edit'),
    # Страница не найдена
    path('404/', views.page_not_found, name='404'),
    # Ошибка сервера
    path('500/', views.server_error, name='500'),
    # Добавление комментария
    path("<username>/<int:post_id>/comment/", views.add_comment, 
         name="add_comment"), 
]
