import os
import re
from html import escape

from jupyter_server.base.handlers import JupyterHandler
from tornado import web


_LITE_ROOT_ATTR = re.compile(r'data-jupyter-lite-root="[^"]*"')


class JupyterLiteStaticHandler(JupyterHandler, web.StaticFileHandler):
    """Serve JupyterLite static files, plus SPA routes, through jupyter-server's auth/XSRF.

    Notebook 7's ``treePathUpdater`` rewrites the URL to ``tree/<subpath>``
    via ``history.pushState`` as the user navigates folders. Those URLs are
    canonical SPA routes owned by the app. A request to a URL under an app
    directory that isn't a concrete asset is a route, not a missing file:
    we render that app's ``index.html`` as the shell, with ``<base href>``
    injected and ``data-jupyter-lite-root`` rewritten to an absolute URL,
    so asset resolution and the ``config-utils.js`` config walk stay
    anchored at the lite root regardless of URL depth.

    Mixing in ``JupyterHandler`` (rather than extending
    ``tornado.web.StaticFileHandler`` alone) keeps auth, origin checks, and
    XSRF cookie issuance on jupyter-server's standard rails. Accessing
    ``self.xsrf_token`` after ``@web.authenticated`` issues the ``_xsrf``
    cookie so that JupyterLite's ``ServerConnection`` can include
    ``X-XSRFToken`` on subsequent POSTs (e.g. via ``serverContentsBaseUrl``)
    and be accepted by jupyter-server's XSRF check.
    """

    auth_resource = "server"

    def initialize(self, path, default_filename=None, lite_prefix=None):
        web.StaticFileHandler.initialize(
            self, path=path, default_filename=default_filename
        )
        self.lite_prefix = lite_prefix

    def set_extra_headers(self, path):
        self.set_header("Cross-Origin-Opener-Policy", "same-origin")
        self.set_header("Cross-Origin-Embedder-Policy", "require-corp")

    @web.authenticated
    async def get(self, path, include_body=True):
        self.xsrf_token  # issue _xsrf cookie for subsequent API POSTs
        if self._is_concrete_file(path):
            return await web.StaticFileHandler.get(
                self, path, include_body=include_body
            )
        app = self._owning_app(path)
        if app is None:
            raise web.HTTPError(404)
        self._serve_app_shell(*app, include_body=include_body)

    def _is_concrete_file(self, path):
        absolute = os.path.join(self.root, path)
        if os.path.isfile(absolute):
            return True
        if os.path.isdir(absolute) and self.default_filename:
            return os.path.isfile(os.path.join(absolute, self.default_filename))
        return False

    def _owning_app(self, path):
        first = path.split("/", 1)[0]
        if not first:
            return None
        root = os.path.abspath(self.root)
        app_dir = os.path.abspath(os.path.join(root, first))
        if not app_dir.startswith(root + os.sep):
            return None
        index = os.path.join(app_dir, "index.html")
        if not os.path.isfile(index):
            return None
        return (first, index)

    def _serve_app_shell(self, app_name, index_path, include_body):
        with open(index_path, encoding="utf-8") as f:
            document = f.read()

        base_href = escape(f"{self.lite_prefix}{app_name}/", quote=True)
        lite_root = escape(self.lite_prefix, quote=True)
        document = document.replace(
            "<head>", f'<head>\n<base href="{base_href}"/>', 1
        )
        document = _LITE_ROOT_ATTR.sub(
            f'data-jupyter-lite-root="{lite_root}"', document
        )

        body = document.encode("utf-8")
        self.set_header("Content-Type", "text/html; charset=UTF-8")
        self.set_header("Content-Length", str(len(body)))
        self.set_header("Cache-Control", "no-store")
        self.set_extra_headers(self.request.path)
        if include_body:
            self.write(body)
