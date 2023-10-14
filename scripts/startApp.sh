#!/bin/bash
cd src
python3 manage.py makemigrations
python3 manage.py migrate
if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi
python3 manage.py runserver 0.0.0.0:8000