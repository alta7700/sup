python manage.py collectstatic --no-input
python manage.py migrate
gunicorn ReportsDjango.wsgi:application -c gunicorn.conf.py