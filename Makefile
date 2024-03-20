.PHONY: install venv freeze dev

venv:
	python3 -m venv .venv
	. .venv/bin/activate

install: venv
	pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt

dev: 
	flask --app flaskr run --debug

start:
	gunicorn -w 4 -b 0.0.0.0:$$PORT flaskr:app