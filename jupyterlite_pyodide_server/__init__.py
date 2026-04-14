"""
JupyterLite Pyodide Server — serve JupyterLite with server-side persistence.

Provides:
- Jupyter Server extension serving JupyterLite at /lite/ with COOP/COEP headers
- JupyterLab extension redirecting /lab to /lite/
- CLI command to build the JupyterLite static site
"""

import os

import tornado.web

from .handlers import JupyterLiteStaticHandler

DEFAULT_OUTPUT_DIR = os.path.join(
    os.path.expanduser("~"), ".local", "share", "jupyterlite"
)
LITE_OUTPUT_DIR = os.environ.get("JUPYTERLITE_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)


def _jupyter_server_extension_points():
    return [{"module": "jupyterlite_pyodide_server"}]


def _load_jupyter_server_extension(server_app):
    web_app = server_app.web_app
    base_url = web_app.settings.get("base_url", "/")

    lite_target = f"{base_url}lite/"
    lite_url = f"{base_url}lite/(.*)"
    handlers = [
        (
            lite_url,
            JupyterLiteStaticHandler,
            {
                "path": LITE_OUTPUT_DIR,
                "default_filename": "index.html",
                "lite_prefix": lite_target,
            },
        ),
    ]
    web_app.add_handlers(".*$", handlers)

    server_app.log.info(
        f"JupyterLite serving from {LITE_OUTPUT_DIR} at {lite_target}"
    )
