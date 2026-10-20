"""``[project.scripts]`` 契约：安装后必须能直接用 ``eltdx`` 命令。

文档（docs/CLI.md）明确写了安装后可用 ``eltdx --help`` / ``eltdx version``，
但 ``[project.scripts]`` 一度没有注册 ``eltdx`` 入口，导致装完只有
``eltdx-smoke`` 等几个旁路命令，主命令反而要退回 ``python -m eltdx``。

这里同时锁三件事：入口已注册、目标可导入且可调用、与 ``python -m eltdx``
走的是同一个 ``main``（两种调用方式等价）。
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"


def _project_scripts() -> dict[str, str]:
    """解析 pyproject 的 [project.scripts]（tomllib 优先，正则兜底）。"""

    text = PYPROJECT.read_text(encoding="utf-8")
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
        tomllib = None  # type: ignore[assignment]
    if tomllib is not None:
        data = tomllib.loads(text)
        return dict(data.get("project", {}).get("scripts", {}))

    # 兜底：逐行解析（仅用于极老解释器）
    section = re.search(r"^\[project\.scripts\]\s*$(.*?)(?=^\[|\Z)", text, re.M | re.S)
    assert section, "pyproject.toml 缺少 [project.scripts]"
    out: dict[str, str] = {}
    for line in section.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def test_eltdx_console_script_is_registered() -> None:
    scripts = _project_scripts()
    assert "eltdx" in scripts, f"[project.scripts] 未注册 eltdx 入口，现有: {sorted(scripts)}"
    assert scripts["eltdx"] == "eltdx.cli:main"


def test_console_script_target_is_importable_and_callable() -> None:
    module_name, _, attr = _project_scripts()["eltdx"].partition(":")
    module = importlib.import_module(module_name)
    target = getattr(module, attr)
    assert callable(target), f"{module_name}:{attr} 不可调用"


def test_console_script_matches_python_dash_m() -> None:
    """两种调用方式必须等价：入口函数与 ``__main__`` 引用的是同一个对象。"""

    main_module = importlib.import_module("eltdx.__main__")
    cli = importlib.import_module("eltdx.cli")
    assert main_module.main is cli.main


def test_console_script_entry_runs() -> None:
    """入口函数本身能跑通（不需要真的安装 console script）。

    选 ``version`` 是因为它不联网、不依赖本机已安装的扩展模块。
    """

    module_name, _, attr = _project_scripts()["eltdx"].partition(":")
    module = importlib.import_module(module_name)
    assert getattr(module, attr)(["version"]) == 0


@pytest.mark.parametrize("argv", [["--help"], ["quote", "--help"]])
def test_console_script_help_exits_zero(argv: list[str]) -> None:
    """help 由 argparse 直接处理，走 ``SystemExit(0)``。"""

    module_name, _, attr = _project_scripts()["eltdx"].partition(":")
    module = importlib.import_module(module_name)
    with pytest.raises(SystemExit) as excinfo:
        getattr(module, attr)(argv)
    assert excinfo.value.code in (0, None)
