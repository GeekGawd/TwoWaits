release: python manage.py makemigrations --no-input
release: python manage.py migrate --no-input

web: gunicorn Project_TwoWaits.wsgi

config:set DISABLE_COLLECTSTATIC=1
