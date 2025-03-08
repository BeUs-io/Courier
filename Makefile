init:
	python3.10 -m venv .venv
	source .venv/bin/activate && python -m pip install --upgrade pip
	source .venv/bin/activate && pip install -r requirements.txt
	source .venv/bin/activate && python manage.py makemigrations
	source .venv/bin/activate && python manage.py makemigrations accounts configuration dashboard
	source .venv/bin/activate && python manage.py migrate
	source .venv/bin/activate && python manage.py initadmin

flake8:
	source .venv/bin/activate && flake8

run:
	source .venv/bin/activate && python manage.py runserver
