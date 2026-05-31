from celery import Celery
import sys
import os

# This line is for discovering tasks by celery(for autodiscover_tasks)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

celery_app = Celery(
    "time_table_worker",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)

celery_app.conf.broker_url = "redis://127.0.0.1:6379/0"
celery_app.conf.result_backend = "redis://127.0.0.1:6379/0"

celery_app.autodiscover_tasks(['apps.time_table_maker'])

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Tehran',
    enable_utc=True,
    task_soft_time_limit=180, # After 180s if the task had not finished and exception would happen.
    task_time_limit=200, 
    task_ack_late=True,
    worker_concurrency=2, # Each worker can run x tasks together.
    worker_prefetch_multiplier=2 # Length of worker's queue.
)
