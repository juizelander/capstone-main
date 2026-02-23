#!/usr/bin/env bash
# exit on error
set -o errexit

python manage.py migrate
python load_initial_data.py
gunicorn capstone.wsgi:application --bind 0.0.0.0:$PORT
