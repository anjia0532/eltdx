"""历史财务数据解析（``gpcw.txt`` 列表 + ``gpcw*.dat`` / ``gpcw*.zip``）。

本模块不依赖任何网络组件，供 :mod:`eltdx.financial` 下载路径复用。
"""

from __future__ import annotations

import struct
import zipfile
from pathlib import Path

from eltdx.exceptions import ResourceFormatError

from .models import FinancialRecord


def parse_financial_file_list(data: bytes) -> list[tuple[str, str, int]]:
    """解析 ``tdxfin/gpcw.txt`` 的内容。

    每行格式：``filename,md5hash,filesize``。

    Returns:
        ``[(filename, hash, filesize), ...]``。
    """

    if not data:
        return []
    text = data.decode("utf-8", errors="replace").strip()
    results: list[tuple[str, str, int]] = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(",")
        if len(parts) < 3:
            continue
        try:
            filesize = int(parts[2])
        except ValueError:
            continue
        results.append((parts[0], parts[1], filesize))
    return results


def parse_financial_dat(
    data: bytes,
    report_date: int = 0,
) -> list[tuple[str, int, int, list[float]]]:
    """解析 ``gpcw*.zip`` 内的 ``.dat`` 二进制文件。

    二进制格式（参考 pytdx.crawler.history_financial_crawler）：

    * Header: 20 字节 ``<1hI1H3L``
        - unknown:     int16
        - report_date: uint32
        - max_count:   uint16   —— 股票索引条目数
        - unknown1:    uint32
        - report_size: uint32   —— 每条股票数据字节长度
        - unknown2:    uint32
    * Index: ``max_count`` 条，每条 11 字节 ``<6s1c1L``
        - code:        6 字节 —— 股票代码
        - market:      1 字节 —— 市场标识（0=SZ, 1=SH）
        - file_offset: uint32 —— 绝对偏移（从文件开头算）
    * Data: 在 ``file_offset`` 位置读取 ``report_size // 4`` 个 ``float32``

    Args:
        data: ``.dat`` 文件的完整字节。
        report_date: 报告期 YYYYMMDD（``0`` 则使用 header 中的值）。

    Returns:
        ``[(code, market_byte, report_date, [float, ...]), ...]``。
    """

    header_fmt = "<1hI1H3L"
    header_size = struct.calcsize(header_fmt)
    if len(data) < header_size:
        return []

    header = struct.unpack(header_fmt, data[:header_size])
    max_count = header[2]
    dat_report_date = header[1]
    report_size = header[4]
    if report_date == 0:
        report_date = dat_report_date

    num_fields = report_size // 4
    if num_fields <= 0:
        return []

    index_fmt = "<6s1c1L"
    index_size = struct.calcsize(index_fmt)
    index_base = header_size
    report_fmt = f"<{num_fields}f"
    report_pack_size = struct.calcsize(report_fmt)

    results: list[tuple[str, int, int, list[float]]] = []
    for i in range(max_count):
        idx_pos = index_base + i * index_size
        if idx_pos + index_size > len(data):
            break
        code_bytes, market_byte, file_offset = struct.unpack(
            index_fmt, data[idx_pos : idx_pos + index_size]
        )
        code = code_bytes.decode("ascii", errors="replace").rstrip("\x00")
        if not code or file_offset == 0:
            continue
        if file_offset + report_pack_size > len(data):
            continue
        floats = list(
            struct.unpack(report_fmt, data[file_offset : file_offset + report_pack_size])
        )
        results.append((code, market_byte[0], report_date, floats))
    return results


def _read_from_zip(zip_path: Path) -> bytes:
    """从 zip 中提取第一个 ``.dat`` 文件内容。"""

    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            for name in archive.namelist():
                if name.endswith(".dat"):
                    return archive.read(name)
    except zipfile.BadZipFile as exc:
        raise ResourceFormatError(f"无效的 zip 文件: {zip_path}") from exc
    raise ResourceFormatError(f"zip 中未找到 .dat 文件: {zip_path}")


def read_history_financial(filepath: str | Path) -> list[FinancialRecord]:
    """从本地 ``gpcw*.dat`` 或 ``gpcw*.zip`` 文件读取历史财务数据。

    Args:
        filepath: ``.dat`` 或 ``.zip`` 文件路径。

    Returns:
        :class:`~eltdx.offline.models.FinancialRecord` 列表。

    Raises:
        FileNotFoundError: 文件不存在。
        ResourceFormatError: 文件格式非法。
    """

    filepath = Path(filepath)
    if not filepath.is_file():
        raise FileNotFoundError(f"历史财务数据文件不存在: {filepath}")

    if filepath.suffix.lower() == ".zip":
        data = _read_from_zip(filepath)
    else:
        data = filepath.read_bytes()

    results: list[FinancialRecord] = []
    for code, market_byte, report_date, fields in parse_financial_dat(data):
        results.append(
            FinancialRecord(
                code=code,
                market_id=market_byte,
                report_date=report_date,
                fields=tuple(fields),
            )
        )
    return results
