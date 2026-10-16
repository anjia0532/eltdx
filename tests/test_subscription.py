"""订阅式实时行情推送（QuoteApi.subscribe / subscribe_hq）测试。"""

from __future__ import annotations

import pytest

from eltdx import TdxClient
from eltdx import hosts as hosts_module
from eltdx.api import QuoteSubscription
from eltdx.hosts import HostProbeResult
from eltdx.models import QuoteRefreshPage, QuoteRefreshRecord
from eltdx.protocol.constants import TYPE_REFRESH_STREAM


@pytest.fixture(autouse=True)
def local_probe_results(tmp_path, monkeypatch):
    monkeypatch.setenv("ELTDX_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(
        hosts_module,
        "probe_host",
        lambda host, **kwargs: HostProbeResult(host=host, ok=True, latency_ms=1.0),
    )


def _record(code: str, price: float) -> QuoteRefreshRecord:
    exchange, number = code[:2], code[2:]
    return QuoteRefreshRecord(
        exchange=exchange,
        market_id=0,
        code=number,
        active=1,
        update_time_raw=153306,
        last_price=price,
        last_close_price=price - 0.1,
        open_price=price - 0.2,
        high_price=price,
        low_price=price - 0.3,
        status_or_reserved_raw=0,
        total_hand=100,
        current_hand=1,
        amount=1000.0,
        amount_raw=0,
        inside_dish=0,
        outer_disc=0,
        unknown_after_outer_raw=0,
        open_amount_raw=0,
        open_amount_yuan=0.0,
        buy_levels=(),
        sell_levels=(),
        tail_raw=b"",
    )


class ScriptedPushTransport:
    """按脚本返回 refresh 首帧与后续 push 帧的最小 transport。"""

    def __init__(self, pushes: list[QuoteRefreshPage | None]) -> None:
        self._pushes = list(pushes)
        self.refresh_calls: list[list[str]] = []
        self.poll_calls: list[float | None] = []

    def connect(self) -> None:
        pass

    def close(self) -> None:
        pass

    def request(self, command: str) -> str:
        return "pong"

    def execute(self, command: int, payload=None):
        assert command == TYPE_REFRESH_STREAM
        codes = list((payload or {}).get("codes") or [])
        self.refresh_calls.append(codes)
        return QuoteRefreshPage(
            tuple(codes),
            tuple(_record(code, 10.0) for code in codes),
            decoded_payload=b"",
        )

    def poll_push(self, timeout: float | None = 0.0, *, parse: bool = False):
        assert parse is True
        self.poll_calls.append(timeout)
        return self._pushes.pop(0) if self._pushes else None


def _client(transport) -> TdxClient:
    return TdxClient(transport=transport)


def test_subscribe_dispatches_initial_snapshot_and_pushes() -> None:
    push = QuoteRefreshPage(
        ("sz000001",),
        (_record("sz000001", 10.5),),
        decoded_payload=b"",
    )
    transport = ScriptedPushTransport([push, None])
    client = _client(transport)

    seen: list[tuple[str, float]] = []

    def on_quote(record) -> None:
        seen.append((record.full_code, record.last_price))

    sub = client.quotes.subscribe(["sh600000", "sz000001"], on_quote)
    assert isinstance(sub, QuoteSubscription)
    assert sub.codes == ("sh600000", "sz000001")

    sub.run(duration=0.0)

    # 首帧快照 2 条 + push 1 条
    assert seen == [
        ("sh600000", 10.0),
        ("sz000001", 10.0),
        ("sz000001", 10.5),
    ]
    assert sub.dispatched == 3
    assert transport.refresh_calls == [["sh600000", "sz000001"]]
    assert sub.stopped is True


def test_run_once_returns_dispatch_count() -> None:
    transport = ScriptedPushTransport([None])
    client = _client(transport)
    sub = client.quotes.subscribe("sz000001", lambda record: None)
    assert sub.run_once() == 0
    assert sub.frames == 1


def test_filter_codes_drops_foreign_records() -> None:
    push = QuoteRefreshPage(
        ("sz000001", "bj430047"),
        (_record("sz000001", 11.0), _record("bj430047", 99.0)),
        decoded_payload=b"",
    )
    transport = ScriptedPushTransport([push, None])
    client = _client(transport)
    seen: list[str] = []
    sub = client.quotes.subscribe(["sz000001"], lambda r: seen.append(r.full_code))
    sub.run(duration=0.0)
    assert seen == ["sz000001", "sz000001"]  # 首帧 + push 中的 sz000001


def test_stop_from_callback_terminates_run() -> None:
    transport = ScriptedPushTransport([None] * 50)
    client = _client(transport)
    holder: dict[str, QuoteSubscription] = {}

    def on_quote(record) -> None:
        holder["sub"].stop()

    sub = client.quotes.subscribe("sz000001", on_quote)
    holder["sub"] = sub
    sub.run(duration=5.0)
    assert sub.stopped is True
    # 首帧派发时即停止，后续一次 poll 都不发生
    assert transport.poll_calls == []


def test_on_error_receives_callback_exception() -> None:
    push = QuoteRefreshPage(
        ("sz000001",),
        (_record("sz000001", 12.0),),
        decoded_payload=b"",
    )
    transport = ScriptedPushTransport([push, None])
    client = _client(transport)
    errors: list[BaseException] = []

    def boom(record) -> None:
        raise RuntimeError("callback failed")

    sub = client.quotes.subscribe("sz000001", boom, on_error=errors.append)
    sub.run(duration=0.0)
    assert len(errors) == 2  # 首帧 + push 各一次
    assert str(errors[0]) == "callback failed"
    assert sub.dispatched == 2


def test_subscribe_hq_is_alias() -> None:
    client = _client(ScriptedPushTransport([]))
    sub = client.quotes.subscribe_hq("sz000001", lambda record: None)
    assert isinstance(sub, QuoteSubscription)


def test_subscribe_rejects_empty_and_non_callable() -> None:
    client = _client(ScriptedPushTransport([]))
    with pytest.raises(ValueError):
        client.quotes.subscribe([], lambda record: None)
    with pytest.raises(ValueError):
        client.quotes.subscribe("   ", lambda record: None)
    with pytest.raises(TypeError):
        client.quotes.subscribe("sz000001", "not-callable")


def test_activate_returns_first_page_and_reactivates() -> None:
    transport = ScriptedPushTransport([])
    client = _client(transport)
    sub = client.quotes.subscribe(["sz000001"], lambda record: None)
    page = sub.activate()
    assert page.count == 1
    assert transport.refresh_calls == [["sz000001"]]
    sub.activate()
    assert transport.refresh_calls == [["sz000001"], ["sz000001"]]


def test_timeout_is_forwarded_to_poll_push() -> None:
    transport = ScriptedPushTransport([None])
    client = _client(transport)
    sub = client.quotes.subscribe("sz000001", lambda record: None, timeout=0.25)
    sub.run_once()
    assert transport.poll_calls == [0.25]
