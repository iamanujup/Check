#!/bin/bash
set -e

gunicorn web:app --bind 0.0.0.0:${PORT:-10000} &

exec python main.py
