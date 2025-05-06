init:
	python -m venv .venv
	.venv\Scripts\activate
	pip install -r requirements.txt

activate:
	.venv\Scripts\activate

server:
	flask run --debug --port 3000

test:
	python test_library_api.py