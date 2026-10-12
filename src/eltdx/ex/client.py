"""扩展行情高层同步客户端 ExTdxClient。"""

from __future__ import annotations

from collections import OrderedDict
from types import TracebackType
from typing import TypeVar

from eltdx._bar_time import (
    BAR_TIME_END,
    BAR_TIME_START,
    align_hour_minute_bars,
    category_to_minutes,
    check_bar_time,
)
from eltdx.ex.commands.base import BaseCommand
from eltdx.ex.commands.get_history_bars_range import GetExHistoryInstrumentBarsRangeCmd
from eltdx.ex.commands.get_instrument_bars import GetExInstrumentBarsCmd
from eltdx.ex.commands.get_instrument_count import GetExInstrumentCountCmd
from eltdx.ex.commands.get_instrument_info import GetExInstrumentInfoCmd
from eltdx.ex.commands.get_instrument_quote import GetExInstrumentQuoteCmd
from eltdx.ex.commands.get_instrument_quote_list import GetExInstrumentQuoteListCmd
from eltdx.ex.commands.get_markets import GetExMarketsCmd
from eltdx.ex.commands.get_minute_time import (
    GetExHistoryMinuteTimeDataCmd,
    GetExMinuteTimeDataCmd,
)
from eltdx.ex.commands.get_transaction import (
    GetExHistoryTransactionDataCmd,
    GetExTransactionDataCmd,
)
from eltdx.ex.hosts import DEFAULT_EX_PORT, KNOWN_EX_HOSTS
from eltdx.ex.models import (
    ExInstrumentBar,
    ExInstrumentInfo,
    ExInstrumentQuote,
    ExMarketInfo,
    ExMinuteBar,
    ExTransactionRecord,
)
from eltdx.ex.transport.sync import ExTdxConnection, ping_ex_all
from eltdx.exceptions import TransportError

_T = TypeVar("_T")


class ExTdxClient:
    """同步扩展行情客户端（期货、港股、外股等，端口 7727）。

    使用示例::

        with ExTdxClient("112.74.214.43") as c:
            print(c.get_instrument_count())
            quote = c.get_instrument_quote(47, "IFL0")

    注意：**不要用 ``get_markets()`` 做首条调用**。实测（含与 easy_tdx 1.20.7 的
    差分对照）所有内置主站都不回应 ``0x23f4``，该调用只会阻塞到超时；需要市场
    清单请直接用 :class:`eltdx.models.enums.ExMarket` 枚举。详见 docs/EXTENDED_MARKET.md。

    未显式指定 ``host`` 时按 ``hosts``（默认 :data:`eltdx.ex.hosts.KNOWN_EX_HOSTS`）
    顺序连接，并在断开时顺序故障转移。
    """

    def __init__(
        self,
        host: str | None = None,
        port: int = DEFAULT_EX_PORT,
        timeout: float = 15.0,
        *,
        hosts: list[str] | None = None,
    ) -> None:
        candidates = list(hosts) if hosts else list(KNOWN_EX_HOSTS)
        if host is not None:
            candidates = [host] + [h for h in candidates if h != host]
        if not candidates:
            raise ValueError("hosts 不能为空")
        self._hosts = candidates
        self._host = host if host is not None else candidates[0]
        self._port = port
        self._timeout = timeout
        self._conn = ExTdxConnection(self._host, port, timeout)
        self._connected = False

    @classmethod
    def from_best_host(
        cls,
        hosts: list[str] | None = None,
        port: int = DEFAULT_EX_PORT,
        timeout: float = 15.0,
        ping_timeout: float = 5.0,
    ) -> "ExTdxClient":
        """测量所有扩展行情服务器延迟，选最低延迟建立连接。"""

        candidates = list(hosts) if hosts else list(KNOWN_EX_HOSTS)
        ranked = ping_ex_all(candidates, port, ping_timeout)
        best = ranked[0][0] if ranked else candidates[0]
        return cls(best, port, timeout, hosts=candidates)

    @staticmethod
    def ping_all(
        hosts: list[str] | None = None,
        port: int = DEFAULT_EX_PORT,
        timeout: float = 5.0,
    ) -> list[tuple[str, float]]:
        """并发测量多台扩展行情服务器延迟，按延迟升序返回。"""

        return ping_ex_all(hosts, port, timeout)

    # ------------------------------------------------------------------ #
    # 连接管理
    # ------------------------------------------------------------------ #

    def connect(self) -> None:
        """建立 TCP 连接；按主机顺序故障转移。"""

        last_exc: TransportError | None = None
        for host in self._ordered_hosts():
            try:
                self._conn = ExTdxConnection(host, self._port, self._timeout)
                self._conn.connect()
            except TransportError as e:
                last_exc = e
                continue
            self._host = host
            self._connected = True
            return
        raise last_exc if last_exc is not None else TransportError("没有可用主机")

    def close(self) -> None:
        """关闭连接。"""

        self._conn.close()
        self._connected = False

    def __enter__(self) -> "ExTdxClient":
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    def _ordered_hosts(self) -> list[str]:
        return [self._host] + [h for h in self._hosts if h != self._host]

    def _execute(self, cmd: "BaseCommand[_T]") -> _T:
        """执行命令；连接断开时按主机顺序故障转移一次。"""

        if not self._connected:
            self.connect()
        try:
            return self._conn.execute(cmd)
        except TransportError:
            self._conn.close()
            self._connected = False
            self.connect()
            return self._conn.execute(cmd)

    # ------------------------------------------------------------------ #
    # 市场信息
    # ------------------------------------------------------------------ #

    def get_markets(self) -> list[ExMarketInfo]:
        """获取扩展行情支持的市场列表。"""

        return self._execute(GetExMarketsCmd())

    def get_instrument_count(self) -> int:
        """获取扩展行情商品总数。"""

        return self._execute(GetExInstrumentCountCmd())

    def get_instrument_info(self, start: int, count: int = 100) -> list[ExInstrumentInfo]:
        """获取商品信息列表（分页）。"""

        return self._execute(GetExInstrumentInfoCmd(start, count))

    # ------------------------------------------------------------------ #
    # 行情
    # ------------------------------------------------------------------ #

    def get_instrument_quote(self, market: int, code: str) -> ExInstrumentQuote | None:
        """获取单个商品五档实时行情。"""

        return self._execute(GetExInstrumentQuoteCmd(market, code))

    def get_instrument_quote_list(
        self,
        market: int,
        category: int,
        start: int = 0,
        count: int = 80,
    ) -> list[OrderedDict[str, object]]:
        """按类别获取商品行情列表。"""

        return self._execute(GetExInstrumentQuoteListCmd(market, category, start, count))

    # ------------------------------------------------------------------ #
    # K线
    # ------------------------------------------------------------------ #

    def get_instrument_bars(
        self,
        category: int,
        market: int,
        code: str,
        start: int = 0,
        count: int = 700,
        *,
        bar_time: str = BAR_TIME_START,
    ) -> list[ExInstrumentBar]:
        """获取K线数据。

        Args:
            bar_time: 时间戳语义。``"start"``（默认）= bar 开始时间（通达信原始，
                上午最后一根 5min 标 ``11:25``、下午第一根标 ``13:00``）；``"end"`` =
                bar 右端点（= 开始 + 周期时长，与 Tushare/同花顺对齐，上午最后一根标
                ``11:30``）。仅对分钟级周期生效；日线及以上不受影响。
        """

        bars = self._execute(GetExInstrumentBarsCmd(category, market, code, start, count))
        return align_hour_minute_bars(
            bars,
            delta_minutes=category_to_minutes(category),
            bar_time=bar_time,
        )

    def get_history_instrument_bars_range(
        self,
        market: int,
        code: str,
        start_date: int,
        end_date: int,
        *,
        bar_time: str = BAR_TIME_START,
    ) -> list[ExInstrumentBar]:
        """按日期范围获取历史K线。

        Args:
            bar_time: 见 :meth:`get_instrument_bars`。本接口**不支持** ``"end"``：
            它只按日期范围查询、不知道周期时长，无法算出右端点，会抛
            :class:`ValueError`（与 easy_tdx 一致）。
        """

        if bar_time == BAR_TIME_END:
            raise ValueError(
                "get_history_instrument_bars_range 不支持 bar_time='end'（缺少周期信息），"
                f"请改用 {BAR_TIME_START!r}"
            )
        check_bar_time(bar_time)
        return self._execute(GetExHistoryInstrumentBarsRangeCmd(market, code, start_date, end_date))

    # ------------------------------------------------------------------ #
    # 分时
    # ------------------------------------------------------------------ #

    def get_minute_time_data(self, market: int, code: str) -> list[ExMinuteBar]:
        """获取当日分时行情数据。"""

        return self._execute(GetExMinuteTimeDataCmd(market, code))

    def get_history_minute_time_data(self, market: int, code: str, date: int) -> list[ExMinuteBar]:
        """获取历史某日分时行情数据（date: YYYYMMDD）。"""

        return self._execute(GetExHistoryMinuteTimeDataCmd(market, code, date))

    # ------------------------------------------------------------------ #
    # 成交
    # ------------------------------------------------------------------ #

    def get_transaction_data(
        self,
        market: int,
        code: str,
        start: int = 0,
        count: int = 1800,
    ) -> list[ExTransactionRecord]:
        """获取当日分笔成交数据。"""

        return self._execute(GetExTransactionDataCmd(market, code, start, count))

    def get_history_transaction_data(
        self,
        market: int,
        code: str,
        date: int,
        start: int = 0,
        count: int = 1800,
    ) -> list[ExTransactionRecord]:
        """获取历史某日分笔成交数据（date: YYYYMMDD）。"""

        return self._execute(GetExHistoryTransactionDataCmd(market, code, date, start, count))



__all__ = ["ExTdxClient"]
