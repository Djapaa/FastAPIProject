import os
import time
from datetime import timedelta

from .settings import settings
from celery import Celery
from celery.schedules import crontab


celery = Celery(__name__)
celery.conf.update(broker_connection_retry_on_startup=True)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", settings.CELERY_BROKER_URL)
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", settings.CELERY_RESULT_BACKEND)
celery.autodiscover_tasks([
    'src.api_v1.auth',
    'src.api_v1.composition'
])


celery.conf.beat_schedule = {
    'calculation_bookmark_rating_votes_every_3_hour':
        {
            'task': 'calculate_bookmarks_ratings_votes_task',
            # 'schedule': timedelta(seconds=30),
            'schedule': crontab(minute=0, hour='*/3'),
        }
}


@celery.task()
def debug_task():
    time.sleep(10)
    print('Hello from debug_task')
