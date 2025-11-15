from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # Главная страница - перенаправляем на список книг
    path('', views.BookListView.as_view(), name='home'),

    # Аутентификация
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/register/', views.register_view, name='register'),
    path('accounts/profile/', views.reader_page, name='reader_page'),

    # Основные URL-ы
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('profile/', views.profile_view, name='profile'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('books/add/', views.BookCreateView.as_view(), name='book_create'),
    path('books/add/author/<int:author_id>/', views.BookCreateForAuthorView.as_view(), name='book_create_for_author'),
    
    # Читатели
    path('readers/', views.reader_list, name='reader_list'),
    path('readers/add/', views.reader_create, name='reader_create'),
    
    # Бронирования
    path('reservations/', views.ReservationListView.as_view(), name='reservation_list'),
    path('reservations/add/', views.BookReservationCreateView.as_view(), name='reservation_create'),
    path('books/<int:book_id>/reserve/', views.book_reserve, name='book_reserve'),
    path('readers/<int:reader_id>/reservations/', views.reader_reservations, name='reader_reservations'),
    
    # Авторы, издательства, жанры
    path('authors/', views.AuthorListView.as_view(), name='author_list'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
    path('publishers/', views.PublisherListView.as_view(), name='publisher_list'),
    path('publishers/<int:pk>/', views.PublisherDetailView.as_view(), name='publisher_detail'),
    path('genres/', views.GenreListView.as_view(), name='genre_list'),
path('manage/users/', views.user_list_view, name='user-list'),
    path('genres/<int:pk>/', views.GenreDetailView.as_view(), name='genre_detail'),
]