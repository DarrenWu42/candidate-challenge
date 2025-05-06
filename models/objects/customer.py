from flask import json

from models.objects import AttributeList, identity

class Customer:
    REQUIRED_ATTRIBUTES: AttributeList = [("name", identity, bool),
                                            ("email", identity, bool),
                                            ("customer_id", identity, bool)]

    def __init__(self, name: str, email: str, customer_id: str):
        self.name: str = name
        self.email: str = email
        self.customer_id: str = customer_id
        self.checkouts: int = 0

    def update_info(self, name: str, email: str):
        self.name = name
        self.email = email

    def checkout_book(self):
        self.checkouts += 1

    def return_book(self):
        self.checkouts -= 1

    def get_response(self):
        return {
            "name": self.name,
            "email": self.email,
            "customer_id": self.customer_id
        }

    def __str__(self):
        return json.dumps(self.get_response())
