#!/bin/bash
cd src
echo "Waiting for postgres..."

while ! nc -z $DJANGO_DATABASE_HOST $DJANGO_DATABASE_PORT; do
    sleep 0.1
done
echo "PostgreSQL started"


python3 manage.py makemigrations
python3 manage.py migrate
if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi



gunicorn academyloadcalculator.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120