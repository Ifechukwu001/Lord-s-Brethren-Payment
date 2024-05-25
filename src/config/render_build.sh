#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install -r requirements.txt
pip install gunicorn uvicorn

# Apply any outstanding database migrations
python src/manage.py migrate