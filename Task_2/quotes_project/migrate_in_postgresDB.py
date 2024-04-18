from quotes.models import Author, Quote  
import psycopg2
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quotes_project.settings")
import django
django.setup()

# Підключення до PostgreSQL
pg_connection = psycopg2.connect(
    dbname='Quotes',
    user='postgres',
    password='GoITHomework7',
    host='localhost'
)

try:
    with pg_connection.cursor() as pg_cursor:
        # Отримання даних з MongoDB та імпорт їх у PostgreSQL
        for author in Author.objects.all():
            # Запис автора в PostgreSQL
            pg_cursor.execute("INSERT INTO autors_list VALUES (%s)", (author.name,))
            # Записи цитат для кожного автора
            for quote in author.quote_set.all():
                pg_cursor.execute("INSERT INTO quote_list (text, autor_id) VALUES (%s, %s)", (quote.text, author.id))

        # Застосування транзакції
        pg_connection.commit()

finally:
    # Закриття з'єднання
    pg_connection.close()