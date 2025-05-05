from http import HTTPStatus
from werkzeug.exceptions import HTTPException
from models.objects.book import Book

class Books():
    def __init__(self):
        self._books: dict[str, Book] = {}

    def reset(self):
        self.__init__()

    def add_book(self, title: str, author: str, isbn: str, copies: int):
        book = None

        # if book exists already, add more copies
        # would need to update if isbn mistakes are plausible
        if isbn in self._books:
            book = self._books[isbn]
            book.add_more_books(copies)
        # otherwise, just add book
        else:
            book = Book(title, author, isbn, copies)
            self._books[isbn] = book

        return book

    def get_book(self, isbn: str):
        if isbn not in self._books:
            e = HTTPException(f"ISBN: {isbn} not found in library!")
            e.code = HTTPStatus.NOT_FOUND
            raise e

        return self._books[isbn]

    def contains_isbn(self, isbn: str):
        return isbn in self._books
