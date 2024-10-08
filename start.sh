#!/usr/bin/env bash

# Start Gunicorn
gunicorn iitbtask.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 4
