# jupyterlite-pyodide-server

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/yacchin1205/jupyterlite-pyodide-server/main)

A pip-installable package that turns any repo2docker / Binder environment into a **JupyterLite workspace with server-side file persistence**.

## Why?

JupyterLite runs entirely in the browser via WebAssembly — no server-side kernel required.
However, by default it stores files in the browser's IndexedDB, which is volatile and device-local.

This package solves that by combining:

- **JupyterLite + Pyodide kernel** — browser-based Python execution
- **[jupyterlite-server-contents](https://github.com/jtpio/jupyterlite-server-contents)** — redirects file storage to the Jupyter Server Contents API running in the same container

The result: users get a lightweight, instantly-loading Python environment where **files are persisted on the server**, surviving browser restarts and accessible from any device.

## How it works

```
Browser (JupyterLite + Pyodide)          Container (Jupyter Server)
┌─────────────────────────────┐          ┌──────────────────────┐
│  Python execution (Wasm)    │          │  File storage        │
│  Notebook UI                │── REST ──│  Contents API        │
│  jupyterlite-server-contents│          │  /api/contents/      │
└─────────────────────────────┘          └──────────────────────┘
```

The package provides:

1. **Server extension** — serves JupyterLite static files at `/lite/` with required COOP/COEP headers for SharedArrayBuffer
2. **Lab extension** — automatically redirects `/lab` to `/lite/`
3. **Build CLI** (`jupyterlite-pyodide-server-build`) — builds the JupyterLite site with `serverContentsBaseUrl` pre-configured to use the same server's Contents API

## Quick start

Add to your Binder-ready repository:

**`binder/environment.yml`**
```yaml
dependencies:
  - python=3.10
  - pip:
    - jupyterlite-pyodide-server
```

**`binder/postBuild`**
```bash
#!/bin/bash
set -ex
jupyterlite-pyodide-server-build
```

That's it. Launch with mybinder.org or `jupyter-repo2docker` and you'll land in a JupyterLite environment with persistent file storage.

## Comparison with related tools

|  | repo2jupyterlite | This package |
|---|---|---|
| Purpose | Distribute notebooks as static sites | Provide a working environment |
| Content | Bundled at build time (static) | Persisted on server (dynamic) |
| Data persistence | None (IndexedDB, volatile) | Server filesystem |
| Infrastructure | Static hosting only | Container with Jupyter Server |

## References

- [JupyterLite](https://jupyterlite.readthedocs.io/)
- [jupyterlite-server-contents](https://github.com/jtpio/jupyterlite-server-contents)
- [Pyodide](https://pyodide.org/)
