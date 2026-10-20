class WebView:
    def load_html(self, html):
        raise NotImplementedError

    def evaluate_js(self, script):
        raise NotImplementedError

    def show(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError