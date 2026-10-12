"""扩展行情同步 TCP 连接（端口 7727）。"""

from __future__ import annotations

import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from types import TracebackType
from typing import TYPE_CHECKING, TypeVar

from eltdx.ex.commands.get_instrument_count import GetExInstrumentCountCmd
from eltdx.ex.frame import HEADER_SIZE, decompress_body, parse_header
from eltdx.ex.hosts import DEFAULT_EX_PORT, KNOWN_EX_HOSTS
from eltdx.exceptions import TransportError

if TYPE_CHECKING:
    from eltdx.ex.commands.base import BaseCommand

_T = TypeVar("_T")

_DEFAULT_TIMEOUT = 15.0


def _first_host() -> str:
    return KNOWN_EX_HOSTS[0]


def ping_ex_host(
    host: str,
    port: int = DEFAULT_EX_PORT,
    timeout: float = 5.0,
) -> float | None:
    """测量单台扩展行情服务器延迟（秒），失败返回 None。"""

    t0 = time.monotonic()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        sock.sendall(GetExInstrumentCountCmd().build_request())
        header_buf = _recv_exact_sock(sock, HEADER_SIZE)
        header = parse_header(header_buf)
        if header.zipsize > 0:
            _recv_exact_sock(sock, header.zipsize)
        return time.monotonic() - t0
    except OSError:
        return None
    finally:
        try:
            sock.close()
        except OSError:
            pass


def ping_ex_all(
    hosts: list[str] | None = None,
    port: int = DEFAULT_EX_PORT,
    timeout: float = 5.0,
) -> list[tuple[str, float]]:
    """并发测量多台扩展行情服务器延迟，按延迟升序返回。"""

    candidates = list(hosts) if hosts else list(KNOWN_EX_HOSTS)
    results: list[tuple[str, float]] = []
    if not candidates:
        return results
    with ThreadPoolExecutor(max_workers=len(candidates)) as pool:
        futures = {pool.submit(ping_ex_host, h, port, timeout): h for h in candidates}
        for fut in as_completed(futures):
            host = futures[fut]
            latency = fut.result()
            if latency is not None:
                results.append((host, latency))
    results.sort(key=lambda item: item[1])
    return results


def _recv_exact_sock(sock: socket.socket, n: int) -> bytes:
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise TransportError("连接被服务器关闭")
        buf.extend(chunk)
    return bytes(buf)


class ExTdxConnection:
    """扩展行情同步 TCP 连接（端口 7727，单包握手）。

    Parameters
    ----------
    mac_ex_mode : bool
        为 True 时自动把 MAC 命令的 head_flag 从 0x1C 转为 0x01，
        以兼容 MAC EX 服务器（要求 head_flag=0x01）。
    """

    def __init__(
        self,
        host: str | None = None,
        port: int = DEFAULT_EX_PORT,
        timeout: float = _DEFAULT_TIMEOUT,
        *,
        mac_ex_mode: bool = False,
    ) -> None:
        self.host = host if host is not None else _first_host()
        self.port = port
        self.timeout = timeout
        self.mac_ex_mode = mac_ex_mode
        self._sock: socket.socket | None = None
        self._lock = threading.Lock()

    def connect(self) -> None:
        """建立 TCP 连接；失败抛 TransportError。"""

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect((self.host, self.port))
        except OSError as e:
            sock.close()
            raise TransportError(f"无法连接 {self.host}:{self.port}: {e}") from e
        self._sock = sock

    def close(self) -> None:
        """关闭连接（幂等）。"""

        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None

    def execute(self, cmd: BaseCommand[_T]) -> _T:
        """执行一条命令：发送请求，接收并解压响应，返回解析结果。"""

        with self._lock:
            sock = self._require_sock()
            request = cmd.build_request()
            if self.mac_ex_mode and request and request[0] == 0x1C:
                request = b"\x01" + request[1:]
            try:
                sock.sendall(request)
                header = parse_header(self._recv_exact(HEADER_SIZE))
                raw_body = self._recv_exact(header.zipsize)
            except OSError as e:
                raise TransportError(f"通信错误: {e}") from e
            body = decompress_body(header, raw_body)
            return cmd.parse_response(body)

    def __enter__(self) -> "ExTdxConnection":
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    def _require_sock(self) -> socket.socket:
        if self._sock is None:
            raise TransportError("未连接，请先调用 connect()")
        return self._sock

    def _recv_exact(self, n: int) -> bytes:
        sock = self._require_sock()
        return _recv_exact_sock(sock, n)


__all__ = ["ExTdxConnection", "ping_ex_host", "ping_ex_all"]
