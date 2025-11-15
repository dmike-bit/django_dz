from django.views.generic import ListView, DetailView, CreateView
from .models import Book, Author, Publisher, Genre, Reader, BookReservation, User
from .forms import BookForm, ReaderForm, BookReservationForm, LoginForm, UserCreationForm, ReaderRegistrationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Case, When, Value, IntegerField
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
def reader_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Требуется аутентификация")
        if not hasattr(request.user, 'reader') or not request.user.reader.is_reader:
            return HttpResponseForbidden("Доступ запрещен")
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.reader.is_admin:
            return HttpResponseForbidden("Доступ запрещен")
        return view_func(request, *args, **kwargs)
    return wrapper
from django.urls import reverse

def login_view(request):
    """Представление для входа пользователя"""
    if request.user.is_authenticated:
        return redirect('library:book_list')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')

                # Редирект по роли
                if user.role == 'admin':
                    return redirect('/admin/')
                elif user.role == 'reader':
                    return redirect('library:reader_page')
                else:  # guest
                    return redirect('library:book_list')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {
        'form': form,
        'title': 'Вход в систему'
    })

def logout_view(request):
    """Представление для выхода пользователя"""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('login')

def register_view(request):
    """Представление для регистрации нового пользователя и читателя"""
    if request.user.is_authenticated:
        return redirect('library:book_list')

    if request.method == 'POST':
        form = ReaderRegistrationForm(request.POST)
        if form.is_valid():
            # Создаем пользователя
            username = form.cleaned_data['email']  # Используем email как username
            password = form.cleaned_data['password']
            user = User.objects.create_user(username=username, email=form.cleaned_data['email'], password=password)
            user.role = 'reader'  # Автоматически устанавливаем роль reader
            user.save()

            # Создаем читателя и связываем с пользователем
            reader = form.save(commit=False)
            reader.user = user
            reader.role = 'reader'  # Автоматически устанавливаем роль reader
            reader.save()

            messages.success(request, f'Аккаунт для {username} успешно создан! Теперь вы можете войти.')
            return redirect('login')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = ReaderRegistrationForm()

    return render(request, 'registration/register.html', {
        'form': form,
        'title': 'Регистрация'
    })

@login_required
def reader_page(request):
    """Личная страница читателя"""
    # Здесь должна быть логика для страницы читателя
    return render(request, 'library/reader_page.html', {
        'title': 'Личная страница'
    })

def book_reserve(request, book_id):
    """Бронирование конкретной книги"""
    book = get_object_or_404(Book, pk=book_id)
    
    # Проверяем доступность книги
    if book.reservations.filter(status='active').exists():
        return render(request, 'library/book_reserve.html', {
            'book': book,
            'title': f'Бронирование книги: {book.title}',
            'readers': Reader.objects.all(),
            'min_date': timezone.now().date(),
            'default_date': timezone.now().date(),
        })
    
    if request.method == 'POST':
        form = BookReservationForm(request.POST, book=book)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.book = book
            reservation.status = 'active'
            
            # Обрабатываем дату из формы
            booking_date_str = request.POST.get('booking_date')
            if booking_date_str:
                try:
                    from datetime import datetime
                    booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d').date()
                    reservation.reservation_date = timezone.make_aware(
                        datetime.combine(booking_date, datetime.min.time())
                    )
                    reservation.end_date = reservation.reservation_date + timezone.timedelta(days=14)
                except (ValueError, TypeError):
                    # Если дата некорректна, используем текущую дату
                    reservation.reservation_date = timezone.now()
                    reservation.end_date = reservation.reservation_date + timezone.timedelta(days=14)
            else:
                reservation.reservation_date = timezone.now()
                reservation.end_date = reservation.reservation_date + timezone.timedelta(days=14)
            
            reservation.save()
            return redirect('library:reader_reservations', reader_id=reservation.reader.pk)
    else:
        form = BookReservationForm(book=book)
    
    return render(request, 'library/book_reserve.html', {
        'form': form,
        'book': book,
        'title': f'Бронирование книги: {book.title}',
        'readers': Reader.objects.all(),
        'min_date': timezone.now().date(),
        'default_date': timezone.now().date(),
    })

def reader_reservations(request, reader_id):
    """Список броней конкретного читателя с сортировкой"""
    reader = get_object_or_404(Reader, pk=reader_id)
    current_date = timezone.now()
    
    reservations = BookReservation.objects.filter(reader=reader).annotate(
        status_priority=Case(
            When(
                status='active',
                end_date__lt=current_date,
                then=Value(1)
            ),
            When(
                status='active',
                end_date__gte=current_date,
                then=Value(2)
            ),
            When(
                status='completed',
                then=Value(3)
            ),
            When(
                status='canceled',
                then=Value(4)
            ),
            output_field=IntegerField(),
        )
    ).order_by('status_priority', '-reservation_date')
    
    return render(request, 'library/reader_reservations.html', {
        'reservations': reservations,
        'reader': reader,
        'current_date': current_date,
    })

def reader_list(request):
    """Список читателей с поиском"""
    search_query = request.GET.get('search', '')
    
    if search_query:
        readers = Reader.objects.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    else:
        readers = Reader.objects.all()
    
    return render(request, 'library/reader_list.html', {
        'readers': readers,
        'search_query': search_query
    })

def reader_create(request):
    """Создание нового читателя"""
    if request.method == 'POST':
        form = ReaderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('library:reader_list')
    else:
        form = ReaderForm()
    
    return render(request, 'library/reader_form.html', {
        'form': form,
        'title': 'Добавить читателя'
    })

class BookReservationCreateView(CreateView):
    """Создание бронирования книги"""
    model = BookReservation
    form_class = BookReservationForm
    template_name = "library/bookreservation_form.html"
    success_url = '/reservations/'

    def form_valid(self, form):
        form.instance.status = 'active'
        return super().form_valid(form)

class ReservationListView(ListView):
    """Список всех бронирований"""
    model = BookReservation
    template_name = "library/bookreservation_list.html"
    context_object_name = "reservations"
    ordering = ['-reservation_date']
    
    def get_queryset(self):
        status_filter = self.request.GET.get('status', '')
        queryset = super().get_queryset()
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.select_related('book', 'reader')

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
        initial = super().get_initial()
        author_id = self.kwargs.get('author_id')
        if author_id:
            initial['authors'] = [author_id]
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author_id = self.kwargs.get('author_id')
        if author_id:
            context['author'] = get_object_or_404(Author, pk=author_id)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
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
        context["published_books"] = Book.objects.filter(publisher=self.object).select_related('publisher').prefetch_related('authors', 'genres')
        return context

# Удалены дублирующие определения GenreListView и GenreDetailView

@reader_required
def profile_view(request):
    """Профиль пользователя"""
    reader = request.user.reader
    return render(request, 'readers/profile.html', {
        'reader': reader,
        'title': 'Мой профиль'
    })

@admin_required
def user_list_view(request):
    """Список пользователей для админа"""
    users = User.objects.all().select_related('reader')
    return render(request, 'admin/users.html', {
        'users': users,
        'title': 'Управление пользователями'
    })

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
        context["books"] = Book.objects.filter(genres=self.object).select_related('publisher').prefetch_related('authors', 'genres')
        return context