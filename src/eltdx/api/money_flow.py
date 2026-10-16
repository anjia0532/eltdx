"""Money-flow API: 7709 daily snapshots plus the 7615 TQLEX history channel."""

from __future__ import annotations

import json
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from eltdx.exceptions import TransportError
from eltdx.models import MoneyFlowBatch, MoneyFlowBlock
from eltdx.models.money_flow import FundFlowRangeSeries
from eltdx.protocol.constants import MAX_KLINE_PAGE_SIZE, TYPE_MONEY_FLOW
from eltdx.protocol.unit import normalize_code, split_code

from .base import ApiBase, _weak_callback

#: 7615 TQLEX 历史资金流向 Entry（``zjlx`` 给 20 日，``zjlx_sj`` 给 3/5/10/20/60 日）。
F10_HISTORY_ENTRY = "CWServ.tdxf10_gg_sj"
#: 服务端接受的历史窗口步长。
HISTORY_DAY_STEPS = (3, 5, 10, 20, 60)
#: 没有 7615 通道时的报错文案。
F10_REQUIRED_MESSAGE = (
    "money_flow.history 需要 7615 F10 通道：请通过 TdxClient 使用，或传入 f10_factory"
)


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
            只连该主机的临时池（用于空数据故障转移）。以弱引用保存，避免子服务与
            ``TdxClient`` 互持形成引用环。
        f10_factory: 可选，无参调用时返回 7615 F10 客户端（``client.f10``），供
            :meth:`history` 使用。同样以弱引用保存；未接线（或回调已失效）时
            :meth:`history` 抛 ``RuntimeError``。
        candidate_hosts: 空数据时按顺序尝试的主机（已按延迟排好序）。
    """

    def __init__(
        self,
        transport,
        *,
        transport_factory=None,
        f10_factory=None,
        candidate_hosts: Sequence[str] = (),
    ) -> None:
        super().__init__(transport)
        self._transport_factory = _weak_callback(transport_factory)
        self._f10_factory = _weak_callback(f10_factory)
        self._candidate_hosts = tuple(candidate_hosts)
        self._dedicated_transport = None
        self._preferred_transport = None
        self._preferred_host: str | None = None
        self._transport_lock = Lock()

    def _resolve_transport_factory(self):
        """解析 ``transport_factory`` 弱引用；回调已随 client 回收时返回 ``None``。"""

        if self._transport_factory is None:
            return None
        return self._transport_factory()

    def _resolve_f10(self):
        """解析并调用 ``f10_factory`` 弱引用，返回 7615 F10 客户端。

        未接线（或回调已随持有者回收）时抛 ``RuntimeError``：``history()`` 没有
        7709 退路，宁可显式报错也不静默返回空数据。
        """

        factory = self._f10_factory() if self._f10_factory is not None else None
        if factory is None:
            raise RuntimeError(F10_REQUIRED_MESSAGE)
        return factory()

    def _active_transport(self):
        # 一旦某台主机被证明「真有数据」，后续查询直接用它，避免每次空返回都重探一轮。
        if self._preferred_transport is not None:
            return self._preferred_transport
        factory = self._resolve_transport_factory()
        if factory is None:
            return self._transport
        with self._transport_lock:
            if self._dedicated_transport is None:
                self._dedicated_transport = factory()
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

    def history(
        self,
        code: str | Sequence[str],
        *,
        days: int = 60,
        start: int = 0,
        count: int | None = None,
        include_raw: bool = False,
        batch_size: int = 75,
    ):
        """历史日资金流向（7615 TQLEX ``CWServ.tdxf10_gg_sj``）。

        与 :meth:`daily` 是两条独立通道：``daily()`` 走 7709 ``0x0ffc``，只给最近
        若干个交易日、但每个交易日带 16 个原始分档值；本方法走 7615 HTTP 网关，
        用 ``{"Params": ["zjlx_sj", code, str(days), code]}`` 取 ``days`` 日窗口的历史。

        !!! warning "为什么不再用 7709 ``0x052d`` category 22"
            原实现走 K 线命令的 22 号周期，实测 18 台可达主站（普通池 + 资金流向专用池）
            对它一律返回 2 字节 ``0000`` 空 payload，而同一连接上的 ``category=4``（日线）
            正常有数据 —— 这是服务端行为，不是本包的缺陷。真实客户端用的是本方法的
            7615 通道，所以 ``history()`` 不再碰 7709，也不做空数据换台。

        Args:
            days: 服务端窗口步长，只接受 ``3`` / ``5`` / ``10`` / ``20`` / ``60``，
                其它值抛 ``ValueError``。
            start: 客户端切片起点（距最新偏移），``0`` 为最新一条。
            count: 客户端切片条数，``None`` 表示 ``start`` 之后的全部；非空时上限
                ``800``（与 K 线同一页大小）。
            include_raw: 是否保留 ``raw_payload``（网关响应重新序列化后的紧凑 JSON 字节）。
            batch_size: 传入代码序列时的最大并发；实际并发不超过连接池容量。

        Returns:
            单只代码返回 :class:`~eltdx.models.money_flow.FundFlowRangeSeries`；代码序列
            返回 ``dict[str, FundFlowRangeSeries]``，键为规范化后的完整代码。

        返回模型的 ``rows`` **原样保留**服务端 ``N00x`` 列（不做语义臆测）：
        ``N001`` 日期、``N002`` 代码、``N003`` 名称、``N004`` 主力净额、
        ``N005`` 超大单净买入、``N006`` 大单净买入、``N007`` 主买净额、
        ``N009`` 上市日期。行序统一为**日期降序（最新在前）**——服务端原始回包
        是升序，客户端已反转，与 :meth:`daily`（``records[0]`` 即最新交易日）
        及 F10 其它日期序列口径一致。
        """

        _validate_batch_size(batch_size)
        _validate_history_days(days)
        _validate_history_start(start)
        if count is not None:
            _validate_history_count(count)
        if isinstance(code, str):
            return self._single_history(
                code,
                days=days,
                start=start,
                count=count,
                include_raw=include_raw,
            )

        codes = [normalize_code(item) for item in code]
        if not codes:
            raise ValueError("codes must not be empty")
        workers = _batch_workers(self._transport, len(codes), batch_size)
        series: dict[str, FundFlowRangeSeries] = {}
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for offset in range(0, len(codes), workers):
                chunk = codes[offset : offset + workers]
                responses = executor.map(
                    lambda item: self._single_history(
                        item,
                        days=days,
                        start=start,
                        count=count,
                        include_raw=include_raw,
                    ),
                    chunk,
                )
                for item, response in zip(chunk, responses):
                    series[item] = response
        return series

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
        recovered = self._recover_empty(
            lambda transport: self._query(transport, code, include_raw), failover
        )
        return response if recovered is None else recovered

    def _single_history(
        self,
        code: str,
        *,
        days: int,
        start: int,
        count: int | None,
        include_raw: bool,
    ) -> FundFlowRangeSeries:
        """一次 7615 ``zjlx_sj`` 请求 + 客户端 ``start`` / ``count`` 切片。"""

        response = self._resolve_f10().params(
            F10_HISTORY_ENTRY,
            "zjlx_sj",
            split_code(code)[2],
            str(days),
            split_code(code)[2],
        )
        # 服务端回包是日期升序（最旧在前，2026-10-15 实测 days=10 首行
        # 2026-09-23、末行 2026-10-14）。统一反转为「最新在前」，与
        # daily()（0x0ffc，records[0] 即最新交易日）和 F10 其它日期序列
        # （ipo_calendar / market_margin_summary / index_members）口径一致；
        # 反转后下面的 start / count 切片（距最新偏移）语义才成立。
        rows = tuple(reversed(response.rows))
        window = rows[start:] if count is None else rows[start : start + count]
        payload = b""
        if include_raw:
            payload = json.dumps(
                response.raw, ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8")
        return FundFlowRangeSeries(
            code=code,
            days=days,
            codes=(split_code(code)[2],),
            rows=window,
            raw_payload=payload,
        )

    def _recover_empty(self, query, failover: _EmptyFailover | None) -> object | None:
        """空数据时逐台主机重试，返回 ``query`` 首个非空结果；全都为空则返回 ``None``。

        **关键语义（与 easy_tdx 一致）**：新股 / 真无数据的标的在所有主机上都是空的，
        此时必须**返回空而不是抛错**，否则会把「本来就没数据」误报成故障。所以本方法
        探测完所有候选主机后返回 ``None``，由调用方原样返回那个空响应。

        ``query`` 接收一个 transport 并返回「非空结果」或 ``None``（空数据）。
        """

        # 「回调本身为 None」与「弱引用已解析不出来（client 已回收）」都走同一降级：
        # 不做故障转移，原样返回空响应。
        if (
            failover is None
            or not self._candidate_hosts
            or self._resolve_transport_factory() is None
        ):
            return None
        with failover.lock:
            if failover.settled:
                if failover.transport is None:
                    # 本轮已确认「所有候选主机都空」，不再为后续标的重复开连接。
                    return None
                return query(failover.transport)
            failover.settled = True
            for host in self._candidate_hosts:
                if host == self._preferred_host:
                    continue  # 已知它对当前数据也空，跳过
                transport = self._open_host_transport(host)
                if transport is None:
                    continue
                try:
                    result = query(transport)
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
        factory = self._resolve_transport_factory()
        if factory is None:
            return None
        try:
            return factory(host)
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


def _validate_history_count(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= MAX_KLINE_PAGE_SIZE:
        raise ValueError(f"count must be between 1 and {MAX_KLINE_PAGE_SIZE}")


def _validate_history_days(value: int) -> None:
    steps = ", ".join(str(step) for step in HISTORY_DAY_STEPS)
    if isinstance(value, bool) or not isinstance(value, int) or value not in HISTORY_DAY_STEPS:
        raise ValueError(f"days must be one of: {steps}")


def _validate_history_start(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("start must be a non-negative integer")
