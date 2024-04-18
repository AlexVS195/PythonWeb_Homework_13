import requests
from bs4 import BeautifulSoup
from quotes.models import Quote

def scrape_quotes(url):
    # Виконуємо запит GET на вказану URL-адресу
    response = requests.get(url)

    # Перевіряємо, чи успішний запит
    if response.status_code == 200:
        # Розбираємо HTML сторінку
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Знаходимо всі цитати на сторінці
        quotes = soup.find_all('blockquote')

        # Ітеруємося по кожній цитаті
        for quote in quotes:
            # Отримуємо текст цитати
            text = quote.text.strip()

            # Отримуємо автора цитати (якщо є)
            author_tag = quote.find('p', class_='author')
            author = author_tag.text.strip() if author_tag else None

            # Зберігаємо цитату в базі даних
            Quote.objects.create(text=text, author=author)

        return True
    else:
        # Якщо запит не вдалий, повертаємо False
        return False
