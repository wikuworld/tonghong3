"""Load Flask shopfloor handlers in-process (no systemd Flask / no :5011)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_LEGACY = Path(__file__).resolve().parents[1] / "legacy"


def load_flask_app():
    if not _LEGACY.is_dir():
        raise RuntimeError(f"Flask shopfloor tree missing: {_LEGACY}")
    legacy = str(_LEGACY)
    if legacy not in sys.path:
        sys.path.insert(0, legacy)
    spec = importlib.util.spec_from_file_location("mrp_flask_shopfloor", _LEGACY / "app.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load Flask shopfloor app.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["mrp_flask_shopfloor"] = module
    sys.modules["app"] = module
    spec.loader.exec_module(module)
    return module.app
