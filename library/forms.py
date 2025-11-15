from django import forms
from .models import Book, Author
from .models import Reader, BookReservation, User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя пользователя'
        }),
        label='Имя пользователя'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль'
        }),
        label='Пароль'
    )

class UserCreationForm(BaseUserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        }),
        label='Email'
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        initial='reader',
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Роль'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Подтверждение пароля'
        })

class ReaderForm(forms.ModelForm):
    class Meta:
        model = Reader
        fields = ['full_name', 'birth_date', 'address', 'phone', 'email']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'full_name': forms.TextInput(attrs={'placeholder': 'Иванов Иван Иванович'}),
            'phone': forms.TextInput(attrs={'placeholder': '+79991234567'}),
        }
        labels = {
            'full_name': 'ФИО читателя',
            'birth_date': 'Дата рождения',
            'address': 'Адрес',
            'phone': 'Номер телефона',
            'email': 'Email',
        }

class BookReservationForm(forms.ModelForm):
    class Meta:
        model = BookReservation
        fields = ['reader']
        widgets = {
            'reader': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'reader': 'Читатель',
        }
    
    def __init__(self, *args, **kwargs):
        self.book = kwargs.pop('book', None)
        super().__init__(*args, **kwargs)
        
        if self.book:
            # Скрываем поле книги, если она передана
            self.fields['book'] = forms.ModelChoiceField(
                queryset=Book.objects.filter(pk=self.book.pk),
                initial=self.book,
                widget=forms.HiddenInput()
            )
    
    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book') or self.book
        reader = cleaned_data.get('reader')
        
        if book and reader:
            # Проверяем, что книга доступна для бронирования
            if book.reservations.filter(status='active').exists():
                raise ValidationError("Эта книга уже забронирована")
            
            # Проверяем, что у читателя нет активных броней на эту книгу
            if reader.has_active_reservation(book):
                raise ValidationError("У этого читателя уже есть активная бронь на эту книгу")
        
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
class ReaderRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Reader
        fields = ['full_name', 'birth_date', 'phone', 'email']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов Иван Иванович'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+79991234567'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@email.com'}),
        }
        labels = {
            'full_name': 'ФИО',
            'birth_date': 'Дата рождения',
            'phone': 'Телефон',
            'email': 'Email',
            'password': 'Пароль',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем обязательность поля cover, если оно есть (но в этой форме его нет)