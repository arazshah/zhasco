#!/bin/sh
set -e
mkdir -p "$DATA_DIR/media"

python manage.py migrate --noinput
# fills empty tables only; never overwrites content edited in the dashboard
python manage.py seed_initial_data
python manage.py ensure_superuser

exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --threads 4 \
  --access-logfile - \
  --forwarded-allow-ips="*"
