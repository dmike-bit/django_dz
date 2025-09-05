from django import forms
from .models import Book, Author
from .models import Reader, BookReservation
from django.core.exceptions import ValidationError
from django.utils import timezone

class ReaderForm(forms.ModelForm):
    class Meta:
        model = Reader
        fields = ['full_name', 'birth_date', 'address', 'phone_number', 'email']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Иванов Иван Иванович'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+79991234567'}),
        }
        labels = {
            'full_name': 'ФИО читателя',
            'birth_date': 'Дата рождения',
            'address': 'Адрес',
            'phone_number': 'Номер телефона',
            'email': 'Email',
        }

class BookReservationForm(forms.ModelForm):
    class Meta:
        model = BookReservation
        fields = ['book', 'reader', 'end_date']
        widgets = {
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'book': forms.Select(attrs={'class': 'form-select'}),
            'reader': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        reader = cleaned_data.get('reader')
        end_date = cleaned_data.get('end_date')
        
        # Проверяем, что книга доступна для бронирования
        if book and book.reservations.filter(status='active').exists():
            raise ValidationError("Эта книга уже забронирована")
        
        # Проверяем, что у читателя нет активных броней на эту книгу
        if reader and book and reader.has_active_reservation(book):
            raise ValidationError("У этого читателя уже есть активная бронь на эту книгу")
        
        # Проверяем, что дата окончания не в прошлом
        if end_date and end_date < timezone.now():
            raise ValidationError("Дата окончания брони не может быть в прошлом")
        
        return cleaned_data

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'isbn', 'description', 'publication_year', 'cover', 'authors', 'publisher', 'genres']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1000,
                'max': 2024
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'cover': forms.FileInput(attrs={'class': 'form-control'}),
            'authors': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'publisher': forms.Select(attrs={'class': 'form-control'}),
            'genres': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настройка выпадающих списков
        self.fields['authors'].queryset = Author.objects.all()
        
        # Добавляем пустой вариант для выбора
        self.fields['publisher'].empty_label = "Выберите издательство"
        
        # Убираем обязательность поля, если нужно
        self.fields['cover'].required = False