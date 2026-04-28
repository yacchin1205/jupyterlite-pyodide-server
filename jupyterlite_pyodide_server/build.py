"""CLI command to build the JupyterLite static site."""

import json
import os
import subprocess
import sys
import tempfile


DEFAULT_OUTPUT_DIR = os.path.join(
    os.path.expanduser("~"), ".local", "share", "jupyterlite"
)


def main():
    output_dir = os.environ.get("JUPYTERLITE_OUTPUT_DIR", DEFAULT_OUTPUT_DIR)

    lite_config = {
        "jupyter-config-data": {
            "serverContentsBaseUrl": "../../",
            "serverContentsToken": "",
            "terminalsAvailable": True,
        }
    }

    cockle_config = {
        "packages": {
            "vim": {},
            "nano": {},
            "tree": {},
        },
        "aliases": {
            "vi": "vim",
        },
    }

    with tempfile.TemporaryDirectory() as build_dir:
        config_path = os.path.join(build_dir, "jupyter-lite.json")
        with open(config_path, "w") as f:
            json.dump(lite_config, f)

        cockle_path = os.path.join(build_dir, "cockle-config-in.json")
        with open(cockle_path, "w") as f:
            json.dump(cockle_config, f)

        cmd = [
            sys.executable, "-m", "jupyter", "lite", "build",
            "--lite-dir", build_dir,
            "--output-dir", output_dir,
        ]

        print(f"Building JupyterLite to {output_dir}")
        subprocess.check_call(cmd)
        print(f"JupyterLite built successfully at {output_dir}")
