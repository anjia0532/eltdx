"""专业财报文件下载与解析（连接通达信"计算服务器"）。

财报数据不在普通行情主站上，而在通达信的"计算服务器"（calc host）上，通过
``0x06B9`` 文件下载指令拉取：

* ``tdxfin/gpcw.txt``          —— 可用财报 zip 列表（filename, md5, size）
* ``tdxfin/gpcwYYYYMMDD.zip``  —— 某一报告期的财报压缩包，内含一个 ``.dat``

下载复用 :class:`eltdx.api.resources.ResourceApi` 的 ``download_file``（其底层即
``0x06B9`` GetReportFileCmd），解析为纯 Python（:mod:`zipfile` + :mod:`struct`）。

鸭子类型（duck typing）要求：:func:`list_archive_files` 与 :func:`download_records`
只要求 ``client`` 暴露 ``client.resources.download_file(path) -> bytes``。任何具备该
形态的对象（含测试替身）都可直接传入；:func:`open_calc_client` 则用真实
:class:`~eltdx.client.TdxClient` 构造指向计算服务器的客户端。
"""

from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

from eltdx.exceptions import ResourceFormatError
from eltdx.offline.history_financial import parse_financial_dat, parse_financial_file_list
from eltdx.offline.models import FinancialFileInfo, FinancialRecord

if TYPE_CHECKING:
    from eltdx.client import TdxClient

__all__ = [
    "CALC_HOSTS",
    "FINANCIAL_LIST_PATH",
    "FinancialFileInfo",
    "FinancialRecord",
    "list_archive_files",
    "download_archive",
    "download_records",
    "open_calc_client",
    "parse_financial_dat",
    "parse_financial_file_list",
]

# 通达信计算服务器（财报下载专用，取自 easy_tdx config._FALLBACK_CALC_HOSTS）。
CALC_HOSTS: tuple[str, ...] = ("120.76.152.87",)

# 财报列表清单路径。
FINANCIAL_LIST_PATH = "tdxfin/gpcw.txt"

_REPORT_DATE_RE = re.compile(r"(\d{8})")


def list_archive_files(client: object) -> list[FinancialFileInfo]:
    """获取可用的历史专业财报文件列表。

    下载并解析计算服务器上的 ``tdxfin/gpcw.txt``。

    Args:
        client: 任意暴露 ``resources.download_file(path) -> bytes`` 的对象
            （如指向计算服务器的 :class:`~eltdx.client.TdxClient`）。

    Returns:
        :class:`FinancialFileInfo` 列表。
    """

    data = client.resources.download_file(FINANCIAL_LIST_PATH)  # type: ignore[attr-defined]
    return [
        FinancialFileInfo(filename=filename, hash=digest, filesize=filesize)
        for filename, digest, filesize in parse_financial_file_list(data)
    ]


def download_archive(client: object, filename: str) -> bytes:
    """从计算服务器下载指定财报 zip 的原始字节。

    Args:
        client: 暴露 ``resources.download_file(path) -> bytes`` 的对象。
        filename: 财报 zip 路径，如 ``"tdxfin/gpcw20260331.zip"``。
    """

    return client.resources.download_file(filename)  # type: ignore[attr-defined]


def download_records(client: object, filename: str) -> list[FinancialRecord]:
    """下载财报 zip → 解出 ``.dat`` → 解析为每只股票的记录。

    Args:
        client: 暴露 ``resources.download_file(path) -> bytes`` 的对象。
        filename: 财报 zip 路径，如 ``"tdxfin/gpcw20260331.zip"``。

    Returns:
        :class:`FinancialRecord` 列表（报告期取自文件名中的 8 位日期）。

    Raises:
        ResourceFormatError: zip 非法或其中不存在 ``.dat`` 文件。
    """

    zip_bytes = download_archive(client, filename)
    if not zip_bytes:
        return []

    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
            dat_names = [name for name in archive.namelist() if name.endswith(".dat")]
            if not dat_names:
                raise ResourceFormatError(f"财报 zip 中未找到 .dat 文件: {filename}")
            dat_data = archive.read(dat_names[0])
    except zipfile.BadZipFile as exc:
        raise ResourceFormatError(f"无效的财报 zip 文件: {filename}") from exc

    match = _REPORT_DATE_RE.search(Path(filename).name)
    report_date = int(match.group(1)) if match else 0

    records: list[FinancialRecord] = []
    for code, market_byte, rdate, fields in parse_financial_dat(dat_data, report_date):
        records.append(
            FinancialRecord(
                code=code,
                market_id=market_byte,
                report_date=rdate,
                fields=tuple(fields),
            )
        )
    return records


def open_calc_client(host: str | None = None, *, timeout: float = 8.0) -> TdxClient:
    """构造一个指向计算服务器的 :class:`~eltdx.client.TdxClient`。

    返回的客户端尚未建立连接；调用方需 ``client.connect()``（或使用
    ``with`` 上下文）后再调用 :func:`list_archive_files` / :func:`download_records`。
    为避免构造期联网探测，这里显式关闭 ``probe_hosts``。

    Args:
        host: 计算服务器地址；为 ``None`` 时使用 :data:`CALC_HOSTS` 第一项。
        timeout: 连接/请求超时秒数。
    """

    from eltdx.client import TdxClient

    return TdxClient(host=host or CALC_HOSTS[0], timeout=timeout, probe_hosts=False)
