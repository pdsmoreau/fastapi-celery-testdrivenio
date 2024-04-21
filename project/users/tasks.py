from celery import shared_task


@shared_task
def divide(x, y):
    import time

    # including comment to teste auto-reload
    time.sleep(5)
    return x / y
