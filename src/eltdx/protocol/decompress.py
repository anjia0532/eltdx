"""有输出上限的 zlib 解压。

行情帧头里的 ``unzipsize`` 只有 2 字节（``<IIIHH``），所以**任何**超过 65535
字节的解压结果都不可能是合法响应。但 :func:`zlib.decompress` 会先把整个输出
分配出来再交给调用方比对长度 —— 一个 8 KB 的压缩体可以先解出 8 MiB，占满内存
之后才抛「长度不符」。

本模块提供 :func:`decompress_limited`，用 ``zlib.decompressobj().decompress(data,
max_length)`` 在**产出过程中**截断，异常响应无法造成过量内存分配。
"""

from __future__ import annotations

import zlib

__all__ = ["MAX_FRAME_UNZIPPED_BYTES", "decompress_limited", "DecompressLimitError"]

#: 帧头 ``unzipsize`` 是 2 字节，合法上限 65535。留一点余量不必要 ——
#: 超过就是异常，直接按这个值封顶既符合协议又足够安全。
MAX_FRAME_UNZIPPED_BYTES = 65535


class DecompressLimitError(Exception):
    """解压输出超过给定上限（尚未读完输入即中止）。"""


def decompress_limited(data: bytes, max_length: int = MAX_FRAME_UNZIPPED_BYTES) -> bytes:
    """解压 ``data``，输出超过 ``max_length`` 立即中止。

    与 :func:`zlib.decompress` 的区别：不等到全部解完才发现超限。命中上限时抛
    :class:`DecompressLimitError`，此时最多只分配了 ``max_length`` 字节。

    Args:
        data: 压缩数据。
        max_length: 输出字节上限。

    Raises:
        DecompressLimitError: 输出达到上限仍未结束（说明实际输出更大）。
        zlib.error: 数据本身不是合法的 zlib 流。
    """

    decompressor = zlib.decompressobj()
    output = decompressor.decompress(data, max_length)
    # unconsumed_tail 非空 = 还有输入没消费完 = 输出已经超限了。
    if decompressor.unconsumed_tail or decompressor.unused_data:
        raise DecompressLimitError(
            f"解压输出超过上限 {max_length} 字节，已中止（声明长度不匹配或响应异常）"
        )
    return output