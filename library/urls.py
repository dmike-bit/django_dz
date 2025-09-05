from django.urls import path
from . import views

app_name = 'library'

urlpatterns = [
    # Существующие URL-ы
    path('books/', views.BookListView.as_view(), name='book_list'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('books/add/', views.BookCreateView.as_view(), name='book_create'),
    path('books/add/author/<int:author_id>/', views.BookCreateForAuthorView.as_view(), name='book_create_for_author'),
    
    # Новые URL-ы для читателей и бронирований
    path('readers/', views.reader_list, name='reader_list'),
    path('readers/add/', views.reader_create, name='reader_create'),
    path('reservations/', views.ReservationListView.as_view(), name='reservation_list'),
    path('reservations/add/', views.BookReservationCreateView.as_view(), name='reservation_create'),
    
    # Остальные URL-ы
    path('authors/', views.AuthorListView.as_view(), name='author_list'),
    path('authors/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
    path('publishers/', views.PublisherListView.as_view(), name='publisher_list'),
    path('publishers/<int:pk>/', views.PublisherDetailView.as_view(), name='publisher_detail'),
    path('genres/', views.GenreListView.as_view(), name='genre_list'),
    path('genres/<int:pk>/', views.GenreDetailView.as_view(), name='genre_detail'),
]