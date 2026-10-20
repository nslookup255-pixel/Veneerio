class Bridge:
    def __init__(self):
        self._functions = {}
        self._event_handlers = {}

    def register(self,name,function):
        self._functions[name] = function
        return function

    def call(self, name, *args, **kwargs):
        function = self._functions.get(name)

        if function is None:
            raise ValueError(f"Unknown bridge function: {name}")

        return function(*args, **kwargs)

    def begin_render(self):
        """Discard event handlers from the previous rendered tree."""
        self._event_handlers.clear()

    def register_event(self, element_id, event_name, callback):
        self._event_handlers[(element_id, event_name)] = callback

    def dispatch_event(self, element_id, event_name, *args, **kwargs):
        callback = self._event_handlers.get((element_id, event_name))
        if callback is None:
            return None
        return callback(*args, **kwargs)

    def javascript_runtime(self):
        from .js import EVENT_RUNTIME

        return EVENT_RUNTIME