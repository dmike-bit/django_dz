from django.views.generic import ListView, DetailView
from .models import Book, Author, Publisher, Genre
from django.db.models import Prefetch


from django.views.generic import CreateView
from django.shortcuts import get_object_or_404
from .forms import BookForm

class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = "library/book_form.html"
    success_url = '/books/'

class BookCreateForAuthorView(CreateView):
    model = Book
    form_class = BookForm
    template_name = "library/book_form.html"
    success_url = '/books/'

    def get_initial(self):
        """Предзаполняем поле автора"""
        initial = super().get_initial()
        author_id = self.kwargs.get('author_id')
        if author_id:
            initial['authors'] = [author_id]
        return initial

    def get_context_data(self, **kwargs):
        """Передаем автора в контекст для отображения в шаблоне"""
        context = super().get_context_data(**kwargs)
        author_id = self.kwargs.get('author_id')
        if author_id:
            context['author'] = get_object_or_404(Author, pk=author_id)
        return context

    def form_valid(self, form):
        """Дополнительная обработка при валидной форме"""
        response = super().form_valid(form)
        # Можно добавить дополнительную логику здесь
        return response

class BookListView(ListView):
    model = Book
    template_name = "library/book_list.html"
    context_object_name = "books"
    ordering = ["title"]
    paginate_by = 10
    
    def get_queryset(self):
        return Book.objects.select_related('publisher').prefetch_related('authors', 'genres')

class BookDetailView(DetailView):
    model = Book
    template_name = "library/book_detail.html"
    context_object_name = "book"
    
    def get_queryset(self):
        return Book.objects.select_related('publisher').prefetch_related('authors', 'genres')

class AuthorListView(ListView):
    model = Author
    template_name = "library/author_list.html"
    context_object_name = "authors"
    ordering = ["full_name"]
    paginate_by = 10

class AuthorDetailView(DetailView):
    model = Author
    template_name = "library/author_detail.html"
    context_object_name = "author"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем книги автора с предзагрузкой связанных данных
        context["books"] = Book.objects.filter(authors=self.object).select_related('publisher').prefetch_related('genres')
        return context

class PublisherListView(ListView):
    model = Publisher
    template_name = "library/publisher_list.html"
    context_object_name = "publishers"
    ordering = ["name"]
    paginate_by = 10

class PublisherDetailView(DetailView):
    model = Publisher
    template_name = "library/publisher_detail.html"
    context_object_name = "publisher"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем книги издательства с предзагрузкой авторов и жанров
        context["published_books"] = Book.objects.filter(publisher=self.object).select_related('publisher').prefetch_related('authors', 'genres')
        return context

class GenreListView(ListView):
    model = Genre
    template_name = "library/genre_list.html"
    context_object_name = "genres"
    ordering = ["name"]
    paginate_by = 15

class GenreDetailView(DetailView):
    model = Genre
    template_name = "library/genre_detail.html"
    context_object_name = "genre"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем книги жанра с предзагрузкой связанных данных
        context["books"] = Book.objects.filter(genres=self.object).select_related('publisher').prefetch_related('authors', 'genres')
        return context
