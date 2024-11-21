import os
from celery import Celery
from .settings import TIME_ZONE

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "afiche.settings")
app = Celery("afiche")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.timezone = TIME_ZONE

app.autodiscover_tasks()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from datetime import timedelta
app.conf.beat_schedule = {
    'check_event_dates': {
        'task': 'event.tasks.check_event_dates',
        'schedule': timedelta(days=1),
    },
}
# python -m celery -A config worker -l info