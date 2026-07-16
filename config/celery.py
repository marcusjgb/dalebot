import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check-upcoming-appointments": {
        "task": "apps.appointments.tasks.check_and_send_reminders",
        "schedule": crontab(minute="*/15"),
    },
    "update-daily-metrics": {
        "task": "apps.analytics.tasks.update_daily_metrics",
        "schedule": crontab(hour=0, minute=5),
    },
}
