"""Contracts for the generated package documentation mirror."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.package.sync_docs import DESTINATION, SOURCE, differences, sync_docs

# ``[text](target.md)`` / ``[text](target.md#anchor)``；跳过外链与站内绝对路径。
_MD_LINK = re.compile(r"\]\(([^)#\s]+\.md)(#[^)\s]*)?\)")


def _broken_links(root: Path) -> list[str]:
    """返回 ``root`` 下所有指向不存在文件的相对 markdown 链接。"""

    broken: list[str] = []
    for md in sorted(root.rglob("*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        for match in _MD_LINK.finditer(text):
            target = match.group(1)
            if target.startswith(("http://", "https://", "/")):
                continue
            if not (md.parent / target).resolve().is_file():
                line = text[: match.start()].count("\n") + 1
                broken.append(f"{md.relative_to(root).as_posix()}:{line} -> {target}")
    return broken


def test_packaged_docs_match_authoritative_root() -> None:
    assert differences(SOURCE, DESTINATION) == ()


def test_docs_have_no_broken_relative_links() -> None:
    """所有文档的相对 ``.md`` 链接必须可达。

    ``mkdocs build --strict`` 会因失效链接直接中止，但它只是 CI 的一个步骤；
    这里前置到测试，避免「文档改了路径、构建才发现」。
    """

    broken = _broken_links(SOURCE)
    assert not broken, "存在失效的相对链接:\n" + "\n".join(broken)


def test_mirror_has_no_broken_relative_links() -> None:
    """镜像目录同样要自洽（它才是打进 wheel 的那一份）。"""

    broken = _broken_links(DESTINATION)
    assert not broken, "镜像存在失效的相对链接:\n" + "\n".join(broken)


def test_sync_docs_copies_and_removes_only_bounded_files(tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    (source / "nested").mkdir(parents=True)
    destination.mkdir()
    (source / "a.md").write_text("a\n", encoding="utf-8")
    (source / "nested" / "b.md").write_text("b\n", encoding="utf-8")
    (destination / "stale.md").write_text("stale\n", encoding="utf-8")

    first = sync_docs(source, destination, check=False, max_changes=2)
    assert len(first.changed) == 2
    assert len(first.remaining) == 1
    second = sync_docs(source, destination, check=False, max_changes=2)
    assert len(second.changed) == 1
    assert second.remaining == ()
    assert differences(source, destination) == ()


def test_check_mode_never_changes_destination(tmp_path: Path) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.mkdir()
    (source / "index.md").write_text("new\n", encoding="utf-8")
    (destination / "index.md").write_text("old\n", encoding="utf-8")

    result = sync_docs(source, destination, check=True, max_changes=None)
    assert result.changed == ()
    assert result.remaining == ("index.md",)
    assert (destination / "index.md").read_text(encoding="utf-8") == "old\n"


def test_sync_rejects_destination_inside_source(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    with pytest.raises(ValueError, match="must not be inside"):
        sync_docs(source, source / "mirror", check=False, max_changes=None)
