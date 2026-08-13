from typing import Callable, Any
from fastapi import BackgroundTasks
import logging

logger = logging.getLogger(__name__)

class TaskDispatcher:
    """
    Abstracts background task execution so business logic doesn't tightly couple to FastAPI's BackgroundTasks.
    Can be easily swapped for Celery, Redis Queue, or RabbitMQ in the future.
    """
    def __init__(self, background_tasks: BackgroundTasks | None = None) -> None:
        self.background_tasks = background_tasks

    def dispatch(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        if self.background_tasks:
            self.background_tasks.add_task(func, *args, **kwargs)
        else:
            logger.warning("No BackgroundTasks provided to TaskDispatcher. Running task synchronously.")
            func(*args, **kwargs)
