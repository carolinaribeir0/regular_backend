from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "check-expiring-docs-every-morning": {
        "task": "regular.tasks.check_expiring_docs_task",
        "schedule": crontab(hour=8, minute=0),  # todo dia às 08:00
    },
}
