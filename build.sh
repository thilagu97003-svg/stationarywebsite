#!/usr/bin/env bash
# Render build script
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py make_placeholders   # only creates files that are still missing
python manage.py seed_data
