#!/bin/sh

until cd /app/
do
    echo "Waiting for server volume..."
done


until python manage.py makemigrations && python manage.py migrate
do
    echo "Waiting for db to be ready..."
    sleep 2
done


python manage.py collectstatic --noinput

python manage.py createsuperuser --username admin --email admin@admin.com --noinput

echo "ENVIRONMENT: $ENVIRON"

if [ "$ENVIRON" = "prod" ]
then
    daphne -b 0.0.0.0 -p 8000 app.asgi:application
elif [ "$ENVIRON" = "local" ]
then
    # for debug
    python manage.py runserver 0.0.0.0:8000
else
    echo "NO VALID ENVIRONMENT AVAILABLE"
fi
