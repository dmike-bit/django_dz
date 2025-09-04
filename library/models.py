from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

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