from datetime import date
from models.objects.checkout import Checkout

class Checkouts:
    def __init__(self):
        # in a database system these would all be different searches
        # for in memory, we'll have to make do
        self._checkouts_by_id: dict[str, Checkout] = {}
        self._checkouts_by_cust_id: dict[str, list[Checkout]] = {}
        self._checkouts_by_isbn_cust_id: dict[tuple[str, str], Checkout] = {}

    def reset(self):
        self.__init__()

    def add_checkout(self, checkout: Checkout):
        isbn = checkout.isbn
        customer_id = checkout.customer_id
        checkout_id = checkout.checkout_id

        checkout.book.checkout_book()
        checkout.customer.checkout_book()

        self._checkouts_by_id[checkout_id] = checkout

        if customer_id not in self._checkouts_by_cust_id:
            self._checkouts_by_cust_id[customer_id] = []
        self._checkouts_by_cust_id[customer_id].append(checkout)

        self._checkouts_by_isbn_cust_id[(isbn, customer_id)] = checkout

    def get_by_id(self, checkout_id: str):
        return self._checkouts_by_id[checkout_id]

    def get_by_customer_id(self, customer_id: str):
        if customer_id not in self._checkouts_by_cust_id: return []
        return self._checkouts_by_cust_id[customer_id]

    def get_by_isbn_cust_id(self, isbn: str, customer_id: str):
        return self._checkouts_by_isbn_cust_id[(isbn, customer_id)]
    
    def contains_isbn_cust_id(self, isbn: str, customer_id: str):
        return (isbn, customer_id) in self._checkouts_by_isbn_cust_id

    def return_book(self, isbn: str, customer_id: str):
        checkout = self.get_by_isbn_cust_id(isbn, customer_id)

        checkout.book.return_book()
        checkout.customer.return_book()

        # remove all checkouts
        del self._checkouts_by_id[checkout.checkout_id]
        del self._checkouts_by_isbn_cust_id[(isbn, customer_id)]
        checkouts = self._checkouts_by_cust_id[customer_id]
        self._checkouts_by_cust_id[customer_id] = \
            [c for c in checkouts if c.checkout_id != checkout.checkout_id]

        response = {
            "message": "Book returned successfully",
            "isbn": checkout.isbn,
            "customer_id": checkout.customer_id,
            "return_date": date.today().isoformat()
        }
        return response
