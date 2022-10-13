python manage.py collectstatic --noinput
gunicorn ReportsDjango.wsgi:application -c gunicorn.conf.py