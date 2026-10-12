"""7709 daily money-flow API."""

from __future__ import annotations

from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from eltdx.exceptions import TransportError
from eltdx.models import MoneyFlowBatch, MoneyFlowBlock
from eltdx.protocol.constants import TYPE_MONEY_FLOW
from eltdx.protocol.unit import normalize_code

from .base import ApiBase


class _EmptyFailover:
    """单次 ``daily()`` 调用内共享的空数据故障转移状态。

    存在的意义是**给重试次数封顶**：服务器「对任何标的都返回空」是**主机级**故障，
    不是标级故障，所以一次 ``daily()`` 里探测一轮就够了；否则一批 75 只票、每只都空时
    会去开 ``75 × 候选主机数`` 条连接。

    ``lock`` 保证多线程批量查询时只有一个线程真正去逐台探测。
    """

    __slots__ = ("lock", "settled", "transport", "host")

    def __init__(self) -> None:
        self.lock = Lock()
        self.settled = False
        self.transport = None
        self.host: str | None = None


class MoneyFlowApi(ApiBase):
    """Read the latest daily money-flow records.

    Args:
        transport: 主 transport。
        transport_factory: 可选，无参调用时返回资金流直连池；带 ``host`` 调用时返回
            只连该主机的临时池（用于空数据故障转移）。
        candidate_hosts: 空数据时按顺序尝试的主机（已按延迟排好序）。
    """

    def __init__(
        self,
        transport,
        *,
        transport_factory=None,
        candidate_hosts: Sequence[str] = (),
    ) -> None:
        super().__init__(transport)
        self._transport_factory = transport_factory
        self._candidate_hosts = tuple(candidate_hosts)
        self._dedicated_transport = None
        self._preferred_transport = None
        self._preferred_host: str | None = None
        self._transport_lock = Lock()

    def _active_transport(self):
        # 一旦某台主机被证明「真有数据」，后续查询直接用它，避免每次空返回都重探一轮。
        if self._preferred_transport is not None:
            return self._preferred_transport
        if self._transport_factory is None:
            return self._transport
        with self._transport_lock:
            if self._dedicated_transport is None:
                self._dedicated_transport = self._transport_factory()
            return self._dedicated_transport

    def close(self) -> None:
        with self._transport_lock:
            if self._dedicated_transport is not None:
                self._dedicated_transport.close()
                self._dedicated_transport = None
            if self._preferred_transport is not None:
                self._preferred_transport.close()
                self._preferred_transport = None
            self._preferred_host = None

    def daily(
        self,
        code: str | Sequence[str],
        *,
        include_raw: bool = False,
        batch_size: int = 75,
    ):
        _validate_batch_size(batch_size)
        if isinstance(code, str):
            failover = _EmptyFailover()
            return self._single(code, include_raw=include_raw, failover=failover)

        codes = [normalize_code(item) for item in code]
        if not codes:
            raise ValueError("codes must not be empty")
        workers = _batch_workers(self._transport, len(codes), batch_size)
        blocks: list[MoneyFlowBlock] = []
        # 整批共享一个 failover：第一只空票触发探测，其余票复用结论。
        failover = _EmptyFailover()
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for start in range(0, len(codes), workers):
                chunk = codes[start : start + workers]
                for response in executor.map(
                    lambda item: self._single(
                        item, include_raw=include_raw, failover=failover
                    ),
                    chunk,
                ):
                    if isinstance(response, MoneyFlowBlock):
                        blocks.append(response)
                    elif isinstance(response, MoneyFlowBatch):
                        blocks.extend(response.blocks)
                    else:
                        return response
        return MoneyFlowBatch(tuple(blocks))

    def _single(self, code: str, *, include_raw: bool, failover: _EmptyFailover | None = None):
        response = self._active_transport().execute(
            TYPE_MONEY_FLOW, {"code": code, "include_raw": include_raw}
        )
        blocks = getattr(response, "blocks", None)
        if blocks is None:
            # 形状不是我们认识的批量响应 —— 这**不是**「空数据」，原样返回、不触发故障转移。
            return response
        if len(blocks) == 1:
            return blocks[0]
        if blocks:
            return response
        # 真正的空数据：可能是这台服务器没有该数据（easy_tdx 同款韧性行为）。
        recovered = self._recover_empty(code, include_raw=include_raw, failover=failover)
        return response if recovered is None else recovered

    def _recover_empty(
        self, code: str, *, include_raw: bool, failover: _EmptyFailover | None
    ) -> object | None:
        """空数据时逐台主机重试，返回首个有数据的结果；全都为空则返回 ``None``。

        **关键语义（与 easy_tdx 一致）**：新股 / 真无数据的标的在所有主机上都是空的，
        此时必须**返回空而不是抛错**，否则会把「本来就没数据」误报成故障。所以本方法
        探测完所有候选主机后返回 ``None``，由调用方原样返回那个空响应。
        """

        if failover is None or not self._candidate_hosts or self._transport_factory is None:
            return None
        with failover.lock:
            if failover.settled:
                if failover.transport is None:
                    # 本轮已确认「所有候选主机都空」，不再为后续标的重复开连接。
                    return None
                return self._query(failover.transport, code, include_raw)
            failover.settled = True
            for host in self._candidate_hosts:
                if host == self._preferred_host:
                    continue  # 已知它对当前数据也空，跳过
                transport = self._open_host_transport(host)
                if transport is None:
                    continue
                try:
                    result = self._query(transport, code, include_raw)
                except TransportError:
                    # 单台主机连不上/超时不该拖垮整个查询，换下一台。
                    _close_quietly(transport)
                    continue
                if result is not None:
                    self._adopt(host, transport)
                    failover.transport = transport
                    failover.host = host
                    return result
                _close_quietly(transport)
            return None

    def _adopt(self, host: str, transport) -> None:
        """记住这台有数据的主机（仅进程内，不落盘；``close()`` 会释放）。"""

        with self._transport_lock:
            if self._preferred_transport is not None:
                return
            self._preferred_transport = transport
            self._preferred_host = host

    def _open_host_transport(self, host: str):
        try:
            return self._transport_factory(host)
        except TransportError:
            return None

    @staticmethod
    def _query(transport, code: str, include_raw: bool) -> object | None:
        """在指定 transport 上查一次；空数据返回 ``None``（供调用方判断换台）。"""

        response = transport.execute(
            TYPE_MONEY_FLOW, {"code": code, "include_raw": include_raw}
        )
        blocks = getattr(response, "blocks", None)
        if blocks is None:
            return None
        if len(blocks) == 1:
            return blocks[0]
        return response if blocks else None


def _close_quietly(transport) -> None:
    try:
        transport.close()
    except Exception:  # noqa: BLE001 - 尽力而为的清理，不能掩盖真正的查询结果
        pass


def _validate_batch_size(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError("batch_size must be a positive integer")


def _batch_workers(transport, code_count: int, batch_size: int) -> int:
    capacity = getattr(transport, "pool_size", 1)
    if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity <= 0:
        capacity = 1
    return min(code_count, batch_size, capacity)
