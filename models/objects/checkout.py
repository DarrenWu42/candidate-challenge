from datetime import date

from flask import json

from models.objects.book import Book
from models.objects.customer import Customer
from models.objects import AttributeList, identity

class Checkout:
    REQUIRED_ATTRIBUTES: AttributeList = [("isbn", identity, bool), 
                                            ("customer_id", identity, bool),
                                            ("due_date", date.fromisoformat, lambda x: x >= date.today())]
    checkout_id = 1

    def __init__(self, book: Book, customer: Customer, isbn: str, customer_id: str, due_date: date):
        # we would be able to get these with sql join, with
        # in memory we'll settle to make our lives easier
        self.book: Book = book
        self.customer: Customer = customer

        self.isbn: str = isbn
        self.customer_id: str = customer_id
        self.checkout_id: str = f"CKO{Checkout.checkout_id}"
        Checkout.checkout_id += 1

        self.checkout_date: date = date.today()
        self.due_date: date = due_date

    def get_response(self):
        return {
            "checkout_id": self.checkout_id,
            "isbn": self.book.isbn,
            "title": self.book.title,
            "customer_id": self.customer_id,
            "checkout_date": date.isoformat(self.checkout_date),
            "due_date": date.isoformat(self.due_date)
        }

    def __str__(self):
        return json.dumps(self.get_response())
