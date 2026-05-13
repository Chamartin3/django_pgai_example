"""Launch Jupyter on the notebooks/ directory for the model comparison walkthrough."""
from __future__ import annotations

import os
from argparse import ArgumentParser
from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Launch Jupyter on the notebooks/ directory"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--port", "-p", type=int, default=8888, help="Port to bind")
        parser.add_argument("--host", default="0.0.0.0", help="Address to bind")
        parser.add_argument(
            "--lab", action="store_true",
            help="Use JupyterLab instead of classic Notebook",
        )
        parser.add_argument(
            "--no-token", action="store_true",
            help="Disable auth token (only for local/container use)",
        )

    def handle(self, *args, **options) -> None:
        notebooks_dir = Path(__file__).resolve().parents[3] / "notebooks"
        notebooks_dir.mkdir(exist_ok=True)

        argv = [
            "jupyter",
            "lab" if options["lab"] else "notebook",
            f"--ServerApp.ip={options['host']}",
            f"--ServerApp.port={options['port']}",
            "--ServerApp.open_browser=False",
            f"--ServerApp.root_dir={notebooks_dir}",
            "--ServerApp.allow_root=True",
        ]
        if options["no_token"]:
            argv += [
                "--ServerApp.token=",
                "--ServerApp.password=",
            ]

        self.stdout.write(self.style.SUCCESS(
            f"Starting Jupyter on http://{options['host']}:{options['port']} "
            f"(root: {notebooks_dir})"
        ))
        os.execvp(argv[0], argv)
