import sys
from datetime import date
from http import HTTPStatus

from werkzeug.exceptions import HTTPException
from flask import Flask, json, request, Response

from models import Book, Customer, Checkout, Books, Customers, Checkouts

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

@app.post("/api/books")
def add_book():
    # attempt to retrieve json from request body
    body = request.json

    app.logger.info(f"add_book: called with {body}")

    # check all required book attributes in request
    for attr in Book.REQUIRED_ATTRIBUTES:
        if attr not in body:
            e = HTTPException(f"Attribute retrieval failed! {attr} not in {body}")
            e.code = HTTPStatus.BAD_REQUEST
            raise e

    # extract book attributes to variables
    title: str = body["title"]
    author: str = body["author"]
    isbn: str = body["isbn"]
    copies: int = body["copies"]

    # check all book attributes are good
    if not title or not author or not isbn or copies < 0:
        e = HTTPException(f"Attribute check failed! One of {Book.REQUIRED_ATTRIBUTES} in {body} is bad!")
        e.code = HTTPStatus.BAD_REQUEST
        raise e

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
    # attempt to retrieve json from request body
    body = request.json
    app.logger.info(f"create_customer: called with {body}")

    # check all required customer attributes in request
    for attr in Customer.REQUIRED_ATTRIBUTES:
        if attr not in body:
            e = HTTPException(f"Attribute retrieval failed! {attr} not in {body}")
            e.code = HTTPStatus.BAD_REQUEST
            raise e

    # extract customer attributes to variables
    name: str = body["name"]
    email: str = body["email"]
    customer_id: str = body["customer_id"]

    # check all customer attributes are good
    if not name or not email or not customer_id:
        e = HTTPException(f"Attribute check failed! One of {Customer.REQUIRED_ATTRIBUTES} in {body} is bad!")
        e.code = HTTPStatus.BAD_REQUEST
        raise e

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
    # attempt to retrieve json from request body
    body = request.json
    app.logger.info(f"checkout_book: called with {body}")

    # check all required checkout attributes in request
    for attr in Checkout.REQUIRED_ATTRIBUTES:
        if attr not in body:
            e = HTTPException(f"Attribute retrieval failed! {attr} not in {body}")
            e.code = HTTPStatus.BAD_REQUEST
            raise e

    # extract checkout attributes to variables
    isbn: str = body["isbn"]
    customer_id: str = body["customer_id"]
    due_date: date = date.fromisoformat(body["due_date"])

    # check all checkout attributes are good
    if not isbn or not customer_id or due_date < date.today():
        e = HTTPException(f"Attribute check failed! One of {Checkout.REQUIRED_ATTRIBUTES} in {body} is bad!")
        e.code = HTTPStatus.BAD_REQUEST
        raise e

    # check if checkout is allowed to happen
    book: Book = library.get_book(isbn)
    if book.available_copies < 1:
        e = HTTPException(f"Not enough copies of book: {book}")
        e.code = HTTPStatus.CONFLICT
        raise e

    customer: Customer = customers.get_customer(customer_id)
    if customer.checkouts > MAX_BOOKS_CHECKED_OUT:
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
    # attempt to retrieve json from request body
    body = request.json
    app.logger.info(f"return_book: called with {body}")

    # check all required return attributes in request
    for attr in ["isbn", "customer_id"]:
        if attr not in body:
            e = HTTPException(f"Attribute retrieval failed! {attr} not in {body}")
            e.code = HTTPStatus.BAD_REQUEST
            raise e

    # extract return attributes to variables
    isbn: str = body["isbn"]
    customer_id: str = body["customer_id"]

    # check all return attributes are good
    if not isbn or not customer_id:
        e = HTTPException(f"Attribute check failed! One of {['isbn', 'customer_id']} in {body} is bad!")
        e.code = HTTPStatus.BAD_REQUEST
        raise e

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
