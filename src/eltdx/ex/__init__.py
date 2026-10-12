"""eltdx.ex — 通达信扩展行情（期货、港股、外股等，端口 7727）。"""

from __future__ import annotations

from eltdx.ex.client import ExTdxClient
from eltdx.ex.enums import ExMarket
from eltdx.ex.hosts import KNOWN_EX_HOSTS, MAC_EX_HOSTS
from eltdx.ex.models import KNOWN_EX_MARKETS

__all__ = [
    "ExTdxClient",
    "MacExClient",
    "ExMarket",
    "KNOWN_EX_HOSTS",
    "KNOWN_EX_MARKETS",
    "MAC_EX_HOSTS",
]


def __getattr__(name: str) -> object:
    """按需导出 MacExClient（其依赖 eltdx.mac 子包）。"""

    if name == "MacExClient":
        from eltdx.ex.mac_client import MacExClient

        return MacExClient
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
