#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create the build directory if it doesn't exist
mkdir -p build

# Collect static files
python manage.py collectstatic --no-input

# Add the project directory to PYTHONPATH
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# Optional: Run migrations
python manage.py migrate