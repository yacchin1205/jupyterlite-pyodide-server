import tornado.web


class JupyterLiteStaticHandler(tornado.web.StaticFileHandler):
    """Serve JupyterLite static files with COOP/COEP headers."""

    def set_extra_headers(self, path):
        self.set_header("Cross-Origin-Opener-Policy", "same-origin")
        self.set_header("Cross-Origin-Embedder-Policy", "require-corp")
