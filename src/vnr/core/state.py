from collections.abc import Callable

from .events import Events


_UNSET = object()

class State:

    def __init__(self, initial_value=_UNSET):
        self._initial_value = initial_value
        self._name = None
        self._data = {}
        self._events = Events()

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self._name is None:
            raise AttributeError("State must be assigned to a class attribute")
        if self._name not in instance._state._data:
            instance._state.set(self._name, self._initial_value)
        return instance._state.get(self._name)

    def __set__(self, instance, value):
        if self._name is None:
            raise AttributeError("State must be assigned to a class attribute")
        instance._state.set(self._name, value)

    def get(self, key):
        if key not in self._data:
            raise KeyError(key)
        return self._data.get(key)

    def set(self, key, value):
        old_value = self._data.get(key)

        if old_value == value and key in self._data:
            return

        self._data[key] = value
        self._events.emit("change", key, old_value, value)

    def on(self, key: str, callback: Callable[..., object]) -> None:
        self._events.on(key, callback)

    def off(self, key: str, callback: Callable[..., object]) -> None:
        self._events.off(key, callback)

    def delete(self, key):
        if key in self._data:
            old_value = self._data.get(key)
            del self._data[key]
            self._events.emit("change", key, old_value, None)