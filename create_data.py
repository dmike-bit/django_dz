from library.models import *

# Создаем тестовых авторов
author1 = Author.objects.create(full_name='Александр Пушкин', birth_date='1799-06-06', biography='Великий русский поэт')
author2 = Author.objects.create(full_name='Лев Толстой', birth_date='1828-09-09', biography='Великий русский писатель')

# Создаем жанры
genre1 = Genre.objects.create(name='Роман')
genre2 = Genre.objects.create(name='Поэзия')

# Создаем издателя
publisher = Publisher.objects.create(name='Издательство Просвещение', country='Россия', foundation_year=1930)

# Создаем книги
book1 = Book.objects.create(
    title='Евгений Онегин',
    isbn='978-5-17-123456-7',
    description='Роман в стихах',
    publication_year=1833,
    publisher=publisher
)
book1.authors.add(author1)
book1.genres.add(genre2)

book2 = Book.objects.create(
    title='Война и мир',
    isbn='978-5-17-765432-1',
    description='Исторический роман',
    publication_year=1869,
    publisher=publisher
)
book2.authors.add(author2)
book2.genres.add(genre1)

print('Тестовые данные созданы успешно!')
