from flask import json

class Book:
    REQUIRED_ATTRIBUTES = ["title", "author", "isbn", "copies"]

    def __init__(self, title: str, author: str, isbn: str, copies: int):
        self.title: str = title
        self.author: str = author
        self.isbn: str = isbn
        self.copies: int = copies
        self.available_copies: int = copies

    def checkout_book(self):
        self.available_copies -= 1

    def return_book(self):
        self.available_copies += 1

    def add_more_books(self, copies):
        self.copies += copies
        self.available_copies += copies

    def get_response(self):
        return {
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "copies": self.copies,
            "available_copies": self.available_copies
        }

    def __str__(self):
        return json.dumps(self.get_response())
