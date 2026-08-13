import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventDispatcher:
    """
    Simple in-memory domain event dispatcher.
    Allows loose coupling between services.
    """
    _listeners: Dict[str, List[Callable[..., Any]]] = {}

    @classmethod
    def subscribe(cls, event_name: str, handler: Callable[..., Any]) -> None:
        if event_name not in cls._listeners:
            cls._listeners[event_name] = []
        if handler not in cls._listeners[event_name]:
            cls._listeners[event_name].append(handler)

    @classmethod
    def publish(cls, event_name: str, *args: Any, **kwargs: Any) -> None:
        logger.info(f"Publishing domain event: {event_name}")
        handlers = cls._listeners.get(event_name, [])
        for handler in handlers:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error executing event handler {handler.__name__} for {event_name}: {e}")
