from typing import Any, Callable

def identity(x): return x
type AttributeValidator = Callable[[Any], bool]
type AttributeTransform = Callable[[Any], Any]
type AttributeList = list[tuple[Any, AttributeTransform, AttributeValidator]]

from .book import Book
from .customer import Customer
from .checkout import Checkout
from.return_book import Return
