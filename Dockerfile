FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DATA_DIR=/app/data PORT=8000

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# collectstatic needs a key at build time only; the real one comes from the environment at runtime
RUN DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput \
 && chmod +x /app/entrypoint.sh

VOLUME ["/app/data"]
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request,os;urllib.request.urlopen('http://127.0.0.1:'+os.environ.get('PORT','8000')+'/robots.txt',timeout=4)" || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
