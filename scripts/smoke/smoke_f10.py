"""Script wrapper for the 7615 TQLEX / F10 smoke check.

优先 import 仓库 ``src/`` 下的 eltdx（未安装时也能跑最新代码）。
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "pyproject.toml").exists())
SRC = ROOT / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from eltdx.f10_smoke import main


if __name__ == "__main__":
    raise SystemExit(main())
