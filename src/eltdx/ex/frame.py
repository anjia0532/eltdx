"""扩展行情响应帧编解码（16 字节帧头 + zlib，纯 Python 实现）。"""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass

from eltdx.exceptions import ProtocolError

HEADER_SIZE: int = 16
_MAGIC: int = 7654321
_HEADER_FMT: str = "<IIIHH"


@dataclass(frozen=True, slots=True)
class FrameHeader:
    """扩展行情响应帧头（16 字节）。"""

    magic: int
    seq_id: int
    method: int
    zipsize: int
    unzipsize: int


def parse_header(buf: bytes) -> FrameHeader:
    """解析 16 字节响应帧头。"""

    if len(buf) < HEADER_SIZE:
        raise ProtocolError(f"响应帧头长度不足: 需要 {HEADER_SIZE}，实际 {len(buf)}")
    try:
        magic, seq_id, method, zipsize, unzipsize = struct.unpack_from(_HEADER_FMT, buf, 0)
    except struct.error as e:  # pragma: no cover - 长度已校验
        raise ProtocolError(f"响应帧头解析失败: {e}") from e
    return FrameHeader(
        magic=magic,
        seq_id=seq_id,
        method=method,
        zipsize=zipsize,
        unzipsize=unzipsize,
    )


def decompress_body(header: FrameHeader, raw_body: bytes) -> bytes:
    """按需 zlib 解压响应 body；长度不符或解压失败抛 ProtocolError。"""

    if len(raw_body) != header.zipsize:
        raise ProtocolError(f"响应 body 长度不符: header={header.zipsize}, actual={len(raw_body)}")
    if header.zipsize == header.unzipsize:
        body = raw_body
    else:
        try:
            body = zlib.decompress(raw_body)
        except zlib.error as e:
            raise ProtocolError(f"响应 body zlib 解压失败: {e}") from e
    if len(body) != header.unzipsize:
        raise ProtocolError(f"响应 body 解压长度不符: header={header.unzipsize}, actual={len(body)}")
    return body


def encode_header(*, seq_id: int, method: int, zipsize: int, unzipsize: int | None = None) -> bytes:
    """构造 16 字节响应帧头（测试/工具用）。"""

    if unzipsize is None:
        unzipsize = zipsize
    return struct.pack(_HEADER_FMT, _MAGIC, seq_id, method, zipsize, unzipsize)


__all__ = ["HEADER_SIZE", "FrameHeader", "parse_header", "decompress_body", "encode_header"]
