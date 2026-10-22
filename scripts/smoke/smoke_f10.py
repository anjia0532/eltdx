"""Script wrapper for the 7615 TQLEX / F10 smoke check.

优先 import 仓库 ``src/`` 下的 eltdx（未安装时也能跑最新代码）；
已安装为 console script（site-packages，无 pyproject.toml）时
直接用安装版，不做 sys.path 注入。
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = next(
    (
        parent / "src"
        for parent in Path(__file__).resolve().parents
        if (parent / "pyproject.toml").is_file() and (parent / "src").is_dir()
    ),
    None,
)
if _SRC is not None and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from eltdx.f10_smoke import main


if __name__ == "__main__":
    raise SystemExit(main())
