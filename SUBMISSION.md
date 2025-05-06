# Submission

## Pre-Requisites

`python==3.13` or `conda`

## Setup

### Recommended Steps

1. `conda create -n candidate-challenge python=3.13 pip`
    - Creates `conda` environment

2. `conda activate candidate-challenge`
    - Activates `conda` environment

### Necessary Steps

1. `make init`
    - Installs requirements using `pip`

## Running

1. `make server`
    - Starts `flask` server in debug mode on port 3000

2. `make test` in another terminal
    - Runs tests for API server

## Assumptions and Trade-Offs

The assumptions and trade-offs listed below are also mentioned in comments in the relevant locations in the code.

1. When `POST`ing when there already exists a `Book` with the same `isbn`, we consider this to be adding more copies of that `Book` to the library.

2. When `POST`ing when there already exists a `Customer` with the same `customer_id`, we consider this to be updating that `Customer` with the new information in the `POST` request.

3. Currently, only in-memory is implemented. However the code is structured to be conducive to a database solution. This is particularly apparent in the `Checkout` class -- which has to hold references to `Book` and `Customer` instead of being able to retrieve this information using an SQL statement -- and the `Checkouts` class -- which has to keep track of several dicts instead of being able to search different columns.
