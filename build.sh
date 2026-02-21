#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Use a dummy SQLite database during collectstatic to prevent Render build failures, 
# since the internal database URL is not accessible during the build phase.
DATABASE_URL=sqlite:///db.sqlite3 python manage.py collectstatic --no-input
