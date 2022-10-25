python manage.py collectstatic --no-input
gunicorn ReportsDjango.wsgi:application -c gunicorn.conf.py