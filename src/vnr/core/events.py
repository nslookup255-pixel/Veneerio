from collections.abc import Callable


class Events:
    def __init__(self):
        self._listeners = {}

    def on(self, event_name: str, listener: Callable[..., object]) -> None:
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(listener)

    def off(self, event_name: str, listener: Callable[..., object]) -> None:
        if event_name in self._listeners:
            self._listeners[event_name].remove(listener)
            if not self._listeners[event_name]:
                del self._listeners[event_name]

    def clear(self):
        self._listeners.clear()

    def once(self, event_name: str, listener: Callable[..., object]) -> None:
        def wrapper(*args, **kwargs):
            self.off(event_name, wrapper)
            listener(*args, **kwargs)

        self.on(event_name, wrapper)

    def emit(self, event_name: str, *args, **kwargs) -> None:
        if event_name in self._listeners:
            for listener in list(self._listeners[event_name]):
                listener(*args, **kwargs)