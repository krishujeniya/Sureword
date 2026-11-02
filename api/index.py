"""Vercel Serverless Function entrypoint for Sureword."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Mark environment as Vercel serverless
os.environ.setdefault("VERCEL", "1")

# Add src to Python module search path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "src"))

from sureword.app import app  # noqa: E402

__all__ = ["app"]
