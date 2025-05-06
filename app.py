from datetime import date
from http import HTTPStatus

from werkzeug.exceptions import HTTPException
from flask import Flask, json, request, Response

from models import Book, Customer, Checkout, Return, Books, Customers, Checkouts

app = Flask(__name__)

MAX_BOOKS_CHECKED_OUT = 5

library: Books = Books()
customers: Customers = Customers()
checkouts: Checkouts = Checkouts()

@app.errorhandler(HTTPException)
def handle_exception(e: HTTPException):
    app.logger.error(str(e))
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

def parse_validate_request(object_type: type[Book | Customer | Checkout | Return]):
    # attempt to retrieve json from request body
    body = request.json

    app.logger.info(f"{request.path}: called with {body}")

    ret_dict = {}

    # check all required book attributes in request
    for attr, transformer, validator in object_type.REQUIRED_ATTRIBUTES:
        if attr not in body:
            e = HTTPException(f"Attribute retrieval failed! {attr} not in {body}")
            e.code = HTTPStatus.BAD_REQUEST
            raise e
        
        attr_value = transformer(body[attr])
        if not validator(attr_value):
            e = HTTPException(f"Attribute validation failed! {attr} in {body} failed check!")
            e.code = HTTPStatus.BAD_REQUEST
            raise e
        
        ret_dict[attr] = attr_value

    return ret_dict

@app.post("/api/books")
def add_book():
    body = parse_validate_request(Book)

    # extract book attributes to variables
    title: str = body["title"]
    author: str = body["author"]
    isbn: str = body["isbn"]
    copies: int = body["copies"]

    # add book to library
    book = library.add_book(title, author, isbn, copies)

    app.logger.info(f"add_book: book created {str(book)}")
    return Response(str(book), status=HTTPStatus.CREATED, mimetype='application/json')

@app.get("/api/books/<isbn>")
def get_book(isbn):
    app.logger.info(f"get_book: called with isbn {isbn}")
    app.logger.info(f"get_book: {str(library.get_book(isbn))}")
    return Response(str(library.get_book(isbn)), status=HTTPStatus.OK, mimetype='application/json')

@app.post("/api/customers")
def create_customer():
    body = parse_validate_request(Customer)

    # extract customer attributes to variables
    name: str = body["name"]
    email: str = body["email"]
    customer_id: str = body["customer_id"]

    # add customer to customers
    customer = customers.add_customer(name, email, customer_id)

    app.logger.info(f"create_customer: customer created {str(customer)}")
    return Response(str(customer), status=HTTPStatus.CREATED, mimetype='application/json')

@app.get("/api/customers/<customer_id>")
def get_customer(customer_id):
    app.logger.info(f"get_customer: called with customer_id {customer_id}")
    app.logger.info(f"get_customer: {str(customers.get_customer(customer_id))}")
    return Response(str(customers.get_customer(customer_id)), status=HTTPStatus.OK, mimetype='application/json')

@app.get("/api/customers/<customer_id>/books")
def get_customer_books(customer_id):
    app.logger.info(f"get_customer_books: called with customer_id {customer_id}")
    _ = customers.get_customer(customer_id)

    customer_checkouts: list[Checkout] = checkouts.get_by_customer_id(customer_id)

    response = list(c.get_response() for c in customer_checkouts)
    app.logger.info(f"get_customer_books: {json.dumps(response)}")

    return Response(json.dumps(response), status=HTTPStatus.OK, mimetype='application/json')

@app.post("/api/checkouts")
def checkout_book():
    body = parse_validate_request(Checkout)

    # extract checkout attributes to variables
    isbn: str = body["isbn"]
    customer_id: str = body["customer_id"]
    due_date: date = body["due_date"]

    # check if checkout is allowed to happen
    book: Book = library.get_book(isbn)
    if book.available_copies < 1:
        e = HTTPException(f"Not enough copies of book: {book}")
        e.code = HTTPStatus.CONFLICT
        raise e

    customer: Customer = customers.get_customer(customer_id)
    if customer.checkouts >= MAX_BOOKS_CHECKED_OUT:
        e = HTTPException(f"Cannot check out more than {MAX_BOOKS_CHECKED_OUT} for customer: {customer}")
        e.code = HTTPStatus.CONFLICT
        raise e

    # create checkout and add
    checkout = Checkout(book, customer, isbn, customer_id, due_date)
    checkouts.add_checkout(checkout)

    app.logger.info(f"checkout_book: checkout created {str(checkout)}")
    return Response(str(checkout), status=HTTPStatus.CREATED, mimetype='application/json')

@app.post("/api/returns")
def return_book():
    body = parse_validate_request(Return)

    # extract return attributes to variables
    isbn: str = body["isbn"]
    customer_id: str = body["customer_id"]

    # check if checkout even exists
    if not checkouts.contains_isbn_cust_id(isbn, customer_id):
        e = HTTPException(f"Checkout with ISBN: {isbn} and customer_id: {customer_id} doesn't exist!")
        e.code = HTTPStatus.CONFLICT
        raise e

    response = checkouts.return_book(isbn, customer_id)
    app.logger.info(f"return_book: book returned {json.dumps(response)}")
    return Response(json.dumps(response), status=HTTPStatus.OK, mimetype='application/json')

@app.post("/api/reset")
def reset_system():
    library.reset()
    customers.reset()
    checkouts.reset()

    response = {"message":"System reset successful"}
    app.logger.info(f"reset_system: system reset")
    return Response(json.dumps(response), HTTPStatus.OK, mimetype='application/json')
