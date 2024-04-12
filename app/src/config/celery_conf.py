import os
import time

from .settings import settings
from celery import Celery

celery = Celery(__name__)
celery.conf.update(broker_connection_retry_on_startup=True)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", settings.CELERY_BROKER_URL)
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", settings.CELERY_RESULT_BACKEND)
celery.autodiscover_tasks([
    'src.api_v1.auth',
])


@celery.task()
def debug_task():
    time.sleep(10)
    print('Hello from debug_task')
