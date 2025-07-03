

from app.tasks.celery_app import celery_app


celery_app.autodiscover_tasks(["app.tasks"])
