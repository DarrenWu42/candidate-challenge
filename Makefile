init:
	pip install -r requirements.txt

server:
	flask run --debug --port 3000

test:
	python test_library_api.py