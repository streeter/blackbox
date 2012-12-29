web: gunicorn blackbox:app
worker: celery worker -A blackbox.tasks --loglevel=info