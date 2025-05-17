from celery import shared_task, chain

# импортируем функции run() из скриптов
from .scripts.adapter import run as adapter_run
from .scripts.cleaner import run as cleaner_run
from .scripts.normalizer import run as normalizer_run


@shared_task
def task_adapter():
    return adapter_run()


@shared_task
def task_cleaner(events):
    return cleaner_run(events)


@shared_task
def task_normalizer(events):
    return normalizer_run(events)


@shared_task
def run_event_pipeline():
    """
    Цепочка: adapter → cleaner → normalizer.
    """
    chain(
        task_adapter.s(),
        task_cleaner.s(),
        task_normalizer.s(),
    )()
