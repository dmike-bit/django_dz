from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from datetime import date, timedelta
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Кастомная модель пользователя"""
    ROLE_CHOICES = [
        ('guest', 'Гость'),
        ('reader', 'Читатель'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='reader',
        verbose_name="Роль"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def has_perm(self, perm):
        """Проверка прав пользователя"""
        if self.role == 'admin':
            return True
        elif self.role == 'reader' and perm in ['reader.view_book', 'reader.reserve_book']:
            return True
        elif self.role == 'guest' and perm in ['guest.view_book_list']:
            return True
        return False


class Reader(models.Model):
    """Модель читателя"""
    ROLE_CHOICES = [
        ('guest', 'Гость'),
        ('reader', 'Читатель'),
        ('admin', 'Администратор')
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, verbose_name="ФИО читателя")
    birth_date = models.DateField(verbose_name="Дата рождения")
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(
        max_length=20,
        verbose_name="Номер телефона",
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Номер телефона должен быть в формате: '+999999999'. До 15 цифр."
            )
        ]
    )
    email = models.EmailField(verbose_name="Email", unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader', verbose_name="Роль")
    registration_date = models.DateTimeField(
        verbose_name="Дата регистрации",
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = "Читатель"
        verbose_name_plural = "Читатели"
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['full_name']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return self.full_name
    
    def get_age(self):
        """Возвращает возраст читателя"""
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    
    def get_active_reservations(self):
        """Возвращает активные брони читателя"""
        return self.reservations.filter(status='active')

    @property
    def is_guest(self):
        return self.role == 'guest'

    @property
    def is_reader(self):
        return self.role == 'reader'

    @property
    def is_admin(self):
        return self.role == 'admin'

    def has_active_reservation(self, book):
        """Проверяет, есть ли у читателя активная бронь на книгу"""
        return self.reservations.filter(book=book, status='active').exists()

class BookReservation(models.Model):
    """Модель бронирования книги"""
    STATUS_CHOICES = [
        ('active', 'Активная'),
        ('completed', 'Завершена'),
        ('canceled', 'Отменена'),
    ]
    
    book = models.ForeignKey(
        'Book',
        on_delete=models.CASCADE,
        verbose_name="Книга",
        related_name="reservations"
    )
    reader = models.ForeignKey(
        Reader,
        on_delete=models.CASCADE,
        verbose_name="Читатель",
        related_name="reservations"
    )
    reservation_date = models.DateTimeField(
        verbose_name="Дата бронирования",
        auto_now_add=True
    )
    end_date = models.DateTimeField(verbose_name="Дата окончания брони")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="Статус"
    )
    
    class Meta:
        verbose_name = "Бронь книги"
        verbose_name_plural = "Брони книг"
        ordering = ['-reservation_date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['end_date']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['book', 'reader'],
                condition=models.Q(status='active'),
                name='unique_active_reservation_per_reader'
            )
        ]
    
    def __str__(self):
        return f"Бронь #{self.id}"
    
    @property
    def is_active(self):
        """Проверяет, активна ли бронь"""
        return self.status == 'active' and timezone.now() < self.end_date
    
    def save(self, *args, **kwargs):
        """Автоматически устанавливаем дату окончания брони при создании"""
        if not self.pk and not self.end_date:
            self.end_date = timezone.now() + timedelta(days=14)  # 2 недели брони
        super().save(*args, **kwargs)

class Genre(models.Model):
    """Модель жанра"""
    name = models.CharField(max_length=100, verbose_name="Название жанра")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Author(models.Model):
    """Модель автора"""
    full_name = models.CharField(max_length=200, verbose_name="ФИО автора")
    birth_date = models.DateField(verbose_name="Дата рождения")
    biography = models.TextField(blank=True, verbose_name="Биография")
    
    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        ordering = ['full_name']
    
    def __str__(self):
        return self.full_name
    
    def get_age(self):
        """Возвращает возраст автора"""
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

class Publisher(models.Model):
    """Модель издательства"""
    name = models.CharField(max_length=200, verbose_name="Название издательства")
    country = models.CharField(max_length=100, verbose_name="Страна")
    foundation_year = models.PositiveIntegerField(
        verbose_name="Год основания",
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(date.today().year)
        ]
    )
    
    class Meta:
        verbose_name = "Издательство"
        verbose_name_plural = "Издательства"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.country})"

class Book(models.Model):
    """Модель книги"""
    title = models.CharField(max_length=200, verbose_name="Название книги")
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    description = models.TextField(blank=True, verbose_name="Описание")
    publication_year = models.PositiveIntegerField(
        verbose_name="Год издания",
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(date.today().year)
        ]
    )
    cover = models.ImageField(
        upload_to='book_covers/',
        blank=True,
        null=True,
        verbose_name="Обложка"
    )
    
    # Связи между моделями
    authors = models.ManyToManyField(Author, verbose_name="Авторы")
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Издательство"
    )
    genres = models.ManyToManyField(Genre, verbose_name="Жанры")

    
    def is_available(self):
        """Проверяет, доступна ли книга для бронирования"""
        return not self.reservations.filter(status='active').exists()
    
    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['publication_year']),
            models.Index(fields=['isbn']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_authors_list(self):
        """Возвращает список авторов в виде строки"""
        return ", ".join([author.full_name for author in self.authors.all()])
    
    def get_genres_list(self):
        """Возвращает список жанров в виде строки"""
        return ", ".join([genre.name for genre in self.genres.all()])