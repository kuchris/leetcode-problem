"""Load a solution module from solutions/ by file name.

Solution files are named ``<frontendId>-<titleSlug>.py``, which is not a valid
Python module name, so tests load them by path instead of importing them.
Contest material lives under ``contest/<contest name>/`` and is loaded by
passing that folder as ``directory``.
"""

import importlib.util
from pathlib import Path

SOLUTIONS_DIR = Path(__file__).resolve().parents[1] / 'solutions'


def load_solution(filename: str, directory: Path | None = None):
    """Return the loaded module for ``filename`` inside ``directory``.

    ``directory`` defaults to ``solutions/``.
    """
    path = (directory or SOLUTIONS_DIR) / filename
    spec = importlib.util.spec_from_file_location(path.stem.replace('-', '_'), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
