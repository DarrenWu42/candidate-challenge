from http import HTTPStatus
from werkzeug.exceptions import HTTPException
from models.objects.customer import Customer

class Customers:
    def __init__(self):
        self._customers: dict[str, Customer] = {}

    def reset(self):
        self.__init__()

    def add_customer(self, name: str, email: str, customer_id: str):
        customer = None

        # if customer exists already, update information
        if customer_id in self._customers:
            customer = self._customers[customer_id]
            customer.update_info(name, email)
        # otherwise, create a new customer
        else:
            customer = Customer(name, email, customer_id)
            self._customers[customer_id] = customer

        return customer

    def get_customer(self, customer_id: str):
        if customer_id not in self._customers:
            e = HTTPException(f"customer_id: {customer_id} not found in customers!")
            e.code = HTTPStatus.NOT_FOUND
            raise e
        return self._customers[customer_id]

    def contains_customer_id(self, customer_id: str):
        return customer_id in self._customers
