from django.contrib import admin
from .models import Book, Author, Publisher, Genre

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_preview')
    search_fields = ('name', 'description')
    list_filter = ('name',)
    
    def description_preview(self, obj):
        return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
    description_preview.short_description = 'Описание'

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'birth_date', 'get_age', 'biography_preview')
    search_fields = ('full_name', 'biography')
    list_filter = ('birth_date',)
    date_hierarchy = 'birth_date'
    
    def get_age(self, obj):
        return obj.get_age()
    get_age.short_description = 'Возраст'
    
    def biography_preview(self, obj):
        return obj.biography[:100] + '...' if len(obj.biography) > 100 else obj.biography
    biography_preview.short_description = 'Биография'

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'foundation_year')
    search_fields = ('name', 'country')
    list_filter = ('country', 'foundation_year')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'isbn', 
        'publication_year', 
        'publisher', 
        'get_authors_list', 
        'get_genres_list',
        'has_cover'
    )
    search_fields = ('title', 'isbn', 'description', 'authors__full_name', 'publisher__name')
    list_filter = (
        'publication_year', 
        'publisher', 
        'genres',
        'authors'
    )
    filter_horizontal = ('authors', 'genres')
    readonly_fields = ('cover_preview',)
    
    def get_authors_list(self, obj):
        return obj.get_authors_list()
    get_authors_list.short_description = 'Авторы'
    
    def get_genres_list(self, obj):
        return obj.get_genres_list()
    get_genres_list.short_description = 'Жанры'
    
    def has_cover(self, obj):
        return bool(obj.cover)
    has_cover.boolean = True
    has_cover.short_description = 'Обложка'
    
    def cover_preview(self, obj):
        if obj.cover:
            return f'<img src="{obj.cover.url}" style="max-height: 200px;" />'
        return "Нет обложки"
    cover_preview.allow_tags = True
    cover_preview.short_description = 'Превью обложки'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('authors', 'genres').select_related('publisher')