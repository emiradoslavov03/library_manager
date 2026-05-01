"""
models.py - Модел за управление на библиотека
"""

from datetime import datetime, timedelta


class Book:
    """Клас, представляващ книга в библиотеката."""

    def __init__(self, title: str, author: str, year: int, genre: str, copies: int = 1):
        self.title = title
        self.author = author
        self.year = year
        self.genre = genre
        self.copies = copies
        self.available_copies = copies
        self.borrowed_by = []  # списък с имена на наематели

    def __repr__(self):
        return f"Book('{self.title}', '{self.author}', {self.year})"

    def __str__(self):
        status = "✅ Налична" if self.available_copies > 0 else "❌ Изчерпана"
        return (
            f"📖 {self.title}\n"
            f"   Автор : {self.author}\n"
            f"   Година: {self.year}\n"
            f"   Жанр  : {self.genre}\n"
            f"   Копия : {self.available_copies}/{self.copies}  {status}"
        )


class Library:
    """Клас, управляващ колекция от книги."""

    def __init__(self, name: str):
        self.name = name
        self.books: list[Book] = []
        self.borrow_log: list[dict] = []   # история на заемания

    #  Метод 1 – добавяне на книга                                        
    def add_book(self, book: Book) -> None:
        """Добавя книга в библиотеката."""
        for existing in self.books:
            if existing.title.lower() == book.title.lower() and \
               existing.author.lower() == book.author.lower():
                existing.copies += book.copies
                existing.available_copies += book.copies
                print(f"[+] Добавени {book.copies} допълнителни копия на '{book.title}'.")
                return
        self.books.append(book)
        print(f"[+] Добавена книга: '{book.title}' от {book.author}.")

    #  Метод 2 – заемане на книга                                         
    def borrow_book(self, title: str, borrower: str, days: int = 14) -> bool:
        """
        Регистрира заемане на книга.
        Връща True при успех, False ако книгата не е намерена / налична.
        """
        book = self._find_book(title)
        if book is None:
            print(f"[!] Книгата '{title}' не е намерена.")
            return False
        if book.available_copies == 0:
            print(f"[!] '{book.title}' не е налична в момента.")
            return False

        book.available_copies -= 1
        book.borrowed_by.append(borrower)
        due_date = datetime.now() + timedelta(days=days)
        self.borrow_log.append({
            "title": book.title,
            "borrower": borrower,
            "borrowed_on": datetime.now().strftime("%Y-%m-%d"),
            "due_date": due_date.strftime("%Y-%m-%d"),
            "returned": False,
        })
        print(f"[✓] '{book.title}' е заета от {borrower}. Върни до: {due_date.strftime('%d.%m.%Y')}.")
        return True

    #  Метод 3 – връщане на книга                                         
    def return_book(self, title: str, borrower: str) -> bool:
        """Регистрира връщане на книга."""
        book = self._find_book(title)
        if book is None:
            print(f"[!] Книгата '{title}' не е намерена.")
            return False
        if borrower not in book.borrowed_by:
            print(f"[!] {borrower} няма заета книга '{title}'.")
            return False

        book.available_copies += 1
        book.borrowed_by.remove(borrower)

        for entry in reversed(self.borrow_log):
            if entry["title"] == book.title and entry["borrower"] == borrower and not entry["returned"]:
                entry["returned"] = True
                entry["returned_on"] = datetime.now().strftime("%Y-%m-%d")
                break

        print(f"[✓] '{book.title}' е върната от {borrower}. Благодарим!")
        return True

    #  Метод 4 – сортиране и показване                                    
    def list_books(self, sort_by: str = "title", only_available: bool = False) -> None:
        """
        Показва всички книги, сортирани по зададен критерий.
        sort_by: 'title' | 'author' | 'year' | 'genre'
        """
        books = [b for b in self.books if b.available_copies > 0] if only_available else self.books

        if not books:
            print("Библиотеката е празна.")
            return

        key_map = {
            "title": lambda b: b.title.lower(),
            "author": lambda b: b.author.lower(),
            "year": lambda b: b.year,
            "genre": lambda b: b.genre.lower(),
        }
        key = key_map.get(sort_by, key_map["title"])
        sorted_books = sorted(books, key=key)

        label = "налични " if only_available else ""
        print(f"\n{'='*50}")
        print(f"  {self.name}  —  {label}книги (сортирани по {sort_by})")
        print(f"{'='*50}")
        for i, book in enumerate(sorted_books, 1):
            print(f"\n{i}. {book}")
        print(f"\n{'='*50}\n")

    #  Метод 5 – търсене                                                 
    def search(self, query: str) -> list[Book]:
        """Търси книги по заглавие, автор или жанр (без да различава регистъра)."""
        q = query.lower()
        results = [
            b for b in self.books
            if q in b.title.lower() or q in b.author.lower() or q in b.genre.lower()
        ]
        if results:
            print(f"\n🔍 Намерени {len(results)} резултат(а) за '{query}':")
            for book in results:
                print(f"\n  {book}")
        else:
            print(f"[!] Не са намерени резултати за '{query}'.")
        return results

    #  Метод 6 – статистика                                   
    def statistics(self) -> None:
        """Отпечатва обобщена статистика за библиотеката."""
        total_titles = len(self.books)
        total_copies = sum(b.copies for b in self.books)
        available = sum(b.available_copies for b in self.books)
        borrowed = total_copies - available
        genres = {}
        for b in self.books:
            genres[b.genre] = genres.get(b.genre, 0) + 1

        print(f"\n{'='*50}")
        print(f"  📊 Статистика — {self.name}")
        print(f"{'='*50}")
        print(f"  Уникални заглавия : {total_titles}")
        print(f"  Общо копия        : {total_copies}")
        print(f"  Налични           : {available}")
        print(f"  Заети в момента   : {borrowed}")
        print(f"\n  Жанрове:")
        for genre, count in sorted(genres.items(), key=lambda x: -x[1]):
            print(f"    • {genre:<20} {count} кн.")
        print(f"{'='*50}\n")

    def _find_book(self, title: str) -> Book | None:
        """Намира книга по (частично) заглавие."""
        title_lower = title.lower()
        for book in self.books:
            if title_lower in book.title.lower():
                return book
        return None