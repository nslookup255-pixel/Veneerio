from .core.component import Component
from .core.icon import resolve_icon_path
from .rendering import HTMLRenderer


class App:
    def __init__(self, title="Kayat App", width=800, height=600, window=None, renderer=None, icon=None):
        self.title = title
        self.width = width
        self.height = height
        self.icon = resolve_icon_path(icon) if icon is not None else None
        self.root = None
        self._mounted = False
        self.window = window
        self.renderer = renderer or HTMLRenderer()

    @property
    def mounted(self):
        return self._mounted

    def mount(self, component):
        if not isinstance(component, Component):
            raise TypeError("App.mount() requires a Component")

        if self._mounted:
            self.unmount()

        self.root = component
        self.root.mount()
        self._mounted = True
        return self.root

    def unmount(self):
        if self.root is not None:
            self.root.unmount()

        self.root = None
        self._mounted = False

    def run(self):
        if self.root is None:
            raise RuntimeError("Cannot run an App without a root Component")

        if not self._mounted:
            self.root.mount()

        if self.window is None:
            from .window import Window

            self.window = Window(self.title, self.width, self.height, icon=self.icon)

        set_bridge = getattr(self.renderer, "set_bridge", None)
        bridge = getattr(self.window, "bridge", None)
        if set_bridge is not None and bridge is not None:
            set_bridge(bridge)
        self.window.load(self.renderer.render(self.root))
        self.window.show()

        return self.root
