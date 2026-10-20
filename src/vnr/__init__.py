from importlib import import_module

__all__ = [
    "App",
    "Component",
    "Element",
    "Events",
    "State",
    "Window",
    "alert",
    "confirm",
    "prompt",
]

_EXPORTS = {
    "App": (".app", "App"),
    "Component": (".core", "Component"),
    "Element": (".core", "Element"),
    "Events": (".core", "Events"),
    "State": (".core", "State"),
    "Window": (".window", "Window"),
    "alert": (".dialogs", "alert"),
    "confirm": (".dialogs", "confirm"),
    "prompt": (".dialogs", "prompt"),
}


def __getattr__(name):
    try:
        module_name, attribute_name = _EXPORTS[name]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None

    value = getattr(import_module(module_name, __name__), attribute_name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(__all__))
