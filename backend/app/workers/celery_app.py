"""
Celery worker configuration and application instance.
"""
import os
from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Initialize Celery app
celery_app = Celery(
    "beraxis_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,       # 1 hour max task time
    task_soft_time_limit=3500,
    worker_prefetch_multiplier=1, # Fair scheduling for long tasks
    broker_connection_retry_on_startup=True
)

# Scheduled Tasks (Beat)
celery_app.conf.beat_schedule = {
    "aggregate-tenant-usage-hourly": {
        "task": "app.workers.tasks.aggregate_usage",
        "schedule": crontab(minute=0), # Run at the top of every hour
    },
    "process-active-campaigns-minutely": {
        "task": "app.workers.tasks.sweep_active_campaigns",
        "schedule": crontab(minute="*"), # Run every minute to check queues
    },
}

if __name__ == "__main__":
    celery_app.start()
