import json
import math
import runpy
import sys
from pathlib import Path


class StateDumpError(RuntimeError):
    pass


def _type_name(value: object) -> str:
    value_type = type(value)
    return f"{value_type.__module__}.{value_type.__qualname__}"


def _safe_repr(value: object) -> str:
    try:
        return repr(value)
    except Exception as error:
        return f"<repr failed: {type(error).__name__}>"


def _serialize_value(value: object, active: set[int] | None = None) -> object:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value

    if active is None:
        active = set()

    value_id = id(value)
    if value_id in active:
        return {"$type": _type_name(value), "$circular": True}

    if isinstance(value, dict):
        active.add(value_id)
        try:
            if all(isinstance(key, str) for key in value):
                return {
                    key: _serialize_value(value[key], active)
                    for key in sorted(value)
                }
            items = [
                [
                    _serialize_value(key, active),
                    _serialize_value(item, active),
                ]
                for key, item in value.items()
            ]
            return {"$type": _type_name(value), "items": items}
        finally:
            active.remove(value_id)

    if isinstance(value, (list, tuple, set, frozenset)):
        active.add(value_id)
        try:
            items = [_serialize_value(item, active) for item in value]
        finally:
            active.remove(value_id)

        if isinstance(value, list):
            return items
        if isinstance(value, (set, frozenset)):
            items.sort(key=lambda item: json.dumps(item, sort_keys=True))
        return {"$type": _type_name(value), "items": items}

    result = {"$type": _type_name(value)}
    if callable(value):
        name = getattr(value, "__name__", None)
        module = getattr(value, "__module__", None)
        if name is not None:
            result["name"] = name
        if module is not None:
            result["module"] = module
    else:
        result["repr"] = _safe_repr(value)
    return result


def _dump_node(node: object, active: set[int]) -> dict[str, object]:
    from ..core.component import Component
    from ..core.element import Element

    node_id = id(node)
    if node_id in active:
        return {
            "kind": "reference",
            "type": _type_name(node),
            "circular": True,
        }

    active.add(node_id)
    try:
        if isinstance(node, Component):
            rendered = node.element
            return {
                "kind": "component",
                "type": _type_name(node),
                "mounted": node.mounted,
                "state": _serialize_value(node.state._data),
                "rendered": (
                    _dump_node(rendered, active) if rendered is not None else None
                ),
            }
        if isinstance(node, Element):
            return {
                "kind": "element",
                "type": _type_name(node),
                "props": _serialize_value(node.props),
                "children": [_dump_node(child, active) for child in node.children],
            }
        raise StateDumpError(f"unsupported node in component tree: {_type_name(node)}")
    finally:
        active.remove(node_id)


def create_state_dump(project_directory: Path) -> dict[str, object]:
    entry_point = project_directory / "main.py"
    if not entry_point.is_file():
        raise StateDumpError(f"application entry point is missing: {entry_point}")

    from ..app import App

    project_path = str(project_directory)
    added_project_path = project_path not in sys.path
    if added_project_path:
        sys.path.insert(0, project_path)
    try:
        namespace = runpy.run_path(str(entry_point), run_name="main")
    except Exception as error:
        raise StateDumpError(
            f"could not load application from {entry_point}: "
            f"{type(error).__name__}: {error}"
        ) from error
    finally:
        if added_project_path and project_path in sys.path:
            sys.path.remove(project_path)

    applications = {
        id(value): value
        for value in namespace.values()
        if isinstance(value, App)
    }
    if not applications:
        raise StateDumpError(f"no App instance found in {entry_point}")
    if len(applications) > 1:
        raise StateDumpError(
            f"multiple App instances found in {entry_point}; "
            "keep a single application instance in the module"
        )

    app = next(iter(applications.values()))
    try:
        root = app.root
        return {
            "schema_version": 1,
            "application": {
                "title": _serialize_value(app.title),
                "width": _serialize_value(app.width),
                "height": _serialize_value(app.height),
                "mounted": app.mounted,
            },
            "root": _dump_node(root, set()) if root is not None else None,
        }
    except Exception as error:
        if isinstance(error, StateDumpError):
            raise
        raise StateDumpError(
            f"could not inspect application state in {entry_point}: "
            f"{type(error).__name__}: {error}"
        ) from error
