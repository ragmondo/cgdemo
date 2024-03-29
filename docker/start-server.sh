#!/bin/bash
echo "In start-server.sh"
echo $PWD

echo "Running migrate and collectstatic"
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

while true
do
    echo "Fetching latest data..."
    python manage.py runscript get_latest_data
    sleep 60
done &

echo "Starting server"

gunicorn cg.wsgi -b "0.0.0.0:8000" --workers=2 --timeout 30
