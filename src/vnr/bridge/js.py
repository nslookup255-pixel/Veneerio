import json


EVENT_RUNTIME = """\
(function () {
    function bindEvents() {
        document.querySelectorAll('[data-kayat-id][data-kayat-event]').forEach(function (element) {
            if (element.dataset.kayatBound === 'true') {
                return;
            }
            element.dataset.kayatBound = 'true';
            element.addEventListener(element.dataset.kayatEvent, function () {
                if (window.pywebview && window.pywebview.api) {
                    window.pywebview.api.dispatch_event(
                        element.dataset.kayatId,
                        element.dataset.kayatEvent,
                        {
                            type: event.type,
                            element_id: element.dataset.kayatId
                        }
                    );
                }
            });
        });
    }

    window.addEventListener('pywebviewready', bindEvents);
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', bindEvents);
    } else {
        bindEvents();
    }
})();
"""


class JS:
    def __init__(self, webview):
        self._webview = webview

    def call(self, name, *args):
        function = "globalThis" + "".join(
            f"[{json.dumps(part)}]" for part in name.split(".")
        )
        arguments = ", ".join(json.dumps(argument) for argument in args)
        script = f"{function}({arguments})"
        return self._webview.evaluate_js(script)