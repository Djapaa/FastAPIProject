import time
from celery import shared_task



@shared_task()
def task_2():
    time.sleep(10)
    return 1