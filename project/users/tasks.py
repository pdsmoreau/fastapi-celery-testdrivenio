import random
import celery
import requests
from asgiref.sync import async_to_sync
from celery import shared_task
from celery.signals import task_postrun
from celery.utils.log import get_task_logger
from project.database import db_context

logger = get_task_logger(__name__)
import logging

from celery.signals import after_setup_logger


@shared_task
def divide(x, y):
    import time

    # including comment to teste auto-reload
    time.sleep(5)
    return x / y


@shared_task
def sample_task(email):
    from project.users.views import api_call

    api_call(email)


# @shared_task(bind=True)
# def task_process_notification(self):
#     try:
#         if not random.choice([0, 1]):
#             # mimic random error

#             raise Exception()
#         requests.post("http://httpbin.org/delay/5")

#     except Exception as e:
#         logger.error("exception raised, it would be retry after 5 seconds")
#         raise self.retry(exc=e, countdown=5)


# @shared_task(
#     bind=True,
#     autoretry_for=(Exception,),
#     retry_kwargs={"max_retries": 7, "countdown": 5},
# )
# def task_process_notification(self):
#     if not random.choice([0, 1]):
#         # mimic random error
#         raise Exception()

#     requests.post("https://httpbin.org/delay/5")


class BaseTaskWithRetry(
    celery.Task
):  # configure celery params in a base class to avoid repeat retry config
    autoretry_for = (Exception, KeyError)
    retry_kwargs = {"max_retries": 5}
    retry_backoff = True


@shared_task(bind=True, base=BaseTaskWithRetry)
def task_process_notification(self):
    raise Exception()


@task_postrun.connect
def task_postrun_handler(task_id, **kwargs):
    from project.ws.views import update_celery_task_status

    async_to_sync(update_celery_task_status)(task_id)

    from project.ws.views import update_celery_task_status_socketio

    update_celery_task_status_socketio(task_id)


@shared_task(name="task_schedule_work")
def task_schedule_work():
    logger.info("task_schedule_work run")


# <QUEUE>:<TASK_NAME>


@shared_task(name="default:dynamic_example_one")
def dynamic_example_one():
    logger.info("Example One")


@shared_task(name="low_priority:dynamic_example_two")
def dynamic_example_two():
    logger.info("Example Two")


@shared_task(name="high_priority:dynamic_example_three")
def dynamic_example_three():
    logger.info("Example Three")


@shared_task()
def task_send_welcome_email(user_pk):
    from project.users.models import User

    with db_context() as session:
        user = session.get(User, user_pk)
        logger.info(f"send email to {user.email} {user.id}")


@shared_task
def task_test_logger():
    logger.info("test")


@after_setup_logger.connect()
def on_after_setup_logger(logger, **kwargs):
    formatter = logger.handlers[0].formatter
    file_handler = logging.FileHandler("celery.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
