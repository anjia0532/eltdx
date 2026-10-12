"""板块数据读取（``.dat`` 板块文件与通达信自定义板块目录）。"""

from __future__ import annotations

from pathlib import Path

from eltdx.exceptions import ResourceFormatError

from .models import BlockInfo, CustomerBlock

# .dat 板块文件：Header 384 字节，Count 2 字节，每条记录 2813 字节（9s+H+H+2800s）
_BLOCK_HEADER_SIZE = 384
_BLOCK_RECORD_SIZE = 2813
_BLOCK_NAME_SIZE = 9
_BLOCK_CODE_SIZE = 7
_BLOCK_CODES_SIZE = 2800
_MAX_BLOCK_CODES = _BLOCK_CODES_SIZE // _BLOCK_CODE_SIZE


def _infer_category(filename: str) -> int:
    """从文件名推断板块分类（0=行业, 1=地域, 2=概念, 3=风格）。"""

    name = filename.lower()
    if "gn" in name:
        return 2
    if "fg" in name:
        return 3
    if "dy" in name:
        return 1
    return 0


def read_block(filepath: str | Path) -> list[BlockInfo]:
    """从本地 ``.dat`` 板块文件读取板块数据。

    格式：Header 384 字节 → Count(2B) → 每条记录 2813 字节
    (名称 9B + 股票数 2B + 类型 2B + 代码区 2800B，每只股票 7B)。

    Args:
        filepath: ``.dat`` 文件路径（如 ``block_zs.dat``）。

    Returns:
        :class:`BlockInfo` 列表。

    Raises:
        FileNotFoundError: 文件不存在。
        ResourceFormatError: 文件头或记录长度非法。
    """

    filepath = Path(filepath)
    if not filepath.is_file():
        raise FileNotFoundError(f"板块数据文件不存在: {filepath}")

    data = filepath.read_bytes()
    if len(data) < _BLOCK_HEADER_SIZE + 2:
        raise ResourceFormatError(f"板块文件头不完整: {filepath}")

    pos = _BLOCK_HEADER_SIZE
    count = int.from_bytes(data[pos : pos + 2], "little")
    pos += 2

    category = _infer_category(filepath.name)
    results: list[BlockInfo] = []
    for _ in range(count):
        if pos + _BLOCK_RECORD_SIZE > len(data):
            break
        name = data[pos : pos + _BLOCK_NAME_SIZE].decode("gbk", errors="replace").strip("\x00")
        stock_count = int.from_bytes(data[pos + 9 : pos + 11], "little")
        codes_start = pos + 13
        codes: list[str] = []
        for i in range(min(stock_count, _MAX_BLOCK_CODES)):
            code_start = codes_start + i * _BLOCK_CODE_SIZE
            code = (
                data[code_start : code_start + _BLOCK_CODE_SIZE]
                .decode("ascii", errors="replace")
                .strip("\x00")
            )
            if code:
                codes.append(code)
        results.append(
            BlockInfo(name=name, category=category, count=stock_count, codes=tuple(codes))
        )
        pos += _BLOCK_RECORD_SIZE

    return results


def read_customer_block(block_dir: str | Path) -> list[CustomerBlock]:
    """从通达信自定义板块目录读取板块数据。

    目录结构：
      ``blocknew.cfg`` — 板块索引（120 字节/条：50B 名称 + 70B 文件名）
      ``*.blk``        — 板块内容（每行一个代码，首位为市场标识）

    Args:
        block_dir: 自定义板块目录路径。

    Returns:
        :class:`CustomerBlock` 列表。

    Raises:
        FileNotFoundError: 目录或 ``blocknew.cfg`` 不存在。
    """

    block_dir = Path(block_dir)
    if not block_dir.is_dir():
        raise FileNotFoundError(f"自定义板块目录不存在: {block_dir}")

    cfg_path = block_dir / "blocknew.cfg"
    if not cfg_path.is_file():
        raise FileNotFoundError(f"板块配置文件不存在: {cfg_path}")

    cfg_data = cfg_path.read_bytes()
    results: list[CustomerBlock] = []
    pos = 0
    while pos + 120 <= len(cfg_data):
        name = cfg_data[pos : pos + 50].decode("gbk", errors="replace").split("\x00")[0]
        blk_filename = (
            cfg_data[pos + 50 : pos + 120].decode("gbk", errors="replace").split("\x00")[0]
        )
        pos += 120
        if not blk_filename:
            continue
        blk_path = block_dir / f"{blk_filename}.blk"
        if not blk_path.is_file() or not name:
            continue
        codes = tuple(
            line.strip()[1:]
            for line in blk_path.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip() and len(line.strip()) > 1
        )
        results.append(
            CustomerBlock(blockname=name, block_type=blk_filename, codes=codes)
        )
    return results
