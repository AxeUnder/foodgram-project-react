python manage.py collectstatic --noinput
python manage.py migrate
python manage.py import_csv
gunicorn foodgram.wsgi:application --bind 0:8080