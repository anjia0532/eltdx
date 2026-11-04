"""``eltdx.protocol.unit`` 的代码/市场规范化测试（纯离线）。

重点覆盖 5xxxxx 号段：缺失时沪市 ETF/LOF/货币基金会被判为
``unable to infer market``，7709 查询直接失败。
"""

from __future__ import annotations

import pytest

from eltdx.exceptions import ProtocolError
from eltdx.protocol.unit import (
    MARKET_TO_ID,
    market_to_id,
    normalize_code,
    normalize_market,
    split_code,
)


def _parse_batch_payload(command, payload, codes):
    from eltdx.protocol import ResponseFrame, parse_command_response

    frame = ResponseFrame(1, 1, command, len(payload), len(payload), payload, b"")
    return parse_command_response(command, frame, {"codes": codes, "include_raw": True})


@pytest.mark.parametrize(
    ("market", "code", "requested", "count"),
    [
        (0, b"\0" * 6, ["sh601059"], 1),
        (1, b'tyle["', ["sh601059"], 1),
        (32, b"600519", ["sh600519"], 1),
        (1, b"600519", ["sh601059"], 1),
        (0, b"000001", ["sh000001"], 1),
        (1, b"600519", ["sh600519"], 2),
        (1, b"600519", ["sh600519", "sh601059"], 2),
    ],
)
def test_finance_rejects_missing_garbage_foreign_and_duplicate_records(market, code, requested, count):
    import struct

    record = bytes([market]) + code + bytes(136)
    with pytest.raises(ProtocolError):
        _parse_batch_payload(0x0010, struct.pack("<H", count) + record * count, requested)


def test_snapshot_partial_reply_must_not_silently_drop_requested_tail():
    from pathlib import Path
    from eltdx.protocol import decode_response

    raw = Path(__file__).parent / "fixtures/7709/snapshots/normal/response.bin"
    payload = decode_response(raw.read_bytes()).data
    with pytest.raises(ProtocolError, match="count"):
        _parse_batch_payload(0x054C, payload, ["sz000001", "sh601059"])


def test_snapshot_valid_foreign_single_is_distinguished_from_garbage():
    from pathlib import Path
    from eltdx.protocol import decode_response

    raw = Path(__file__).parent / "fixtures/7709/snapshots/normal/response.bin"
    payload = decode_response(raw.read_bytes()).data
    with pytest.raises(ProtocolError, match="snapshot missing requested record:"):
        _parse_batch_payload(0x054C, payload, ["sh600002"])
    with pytest.raises(ProtocolError) as caught:
        _parse_batch_payload(0x054C, payload[:13], ["sh600002"])
    assert "snapshot missing requested record:" not in str(caught.value)


def test_snapshot_zero_count_with_garbage_tail_is_not_an_empty_response():
    with pytest.raises(ProtocolError, match="trailing"):
        _parse_batch_payload(0x054C, b"\0\0\0\0garbage-record-body", ["sh600002"])


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        # 沪市 A 股 / 科创板
        ("600000", "sh600000"),
        ("601398", "sh601398"),
        ("688981", "sh688981"),
        # 沪市基金 / ETF / LOF / 货币基金 / 权证（本轮补全的号段）
        ("510300", "sh510300"),
        ("511360", "sh511360"),
        ("512880", "sh512880"),
        ("513180", "sh513180"),
        ("515180", "sh515180"),
        ("518850", "sh518850"),
        ("501050", "sh501050"),
        ("502050", "sh502050"),
        ("580000", "sh580000"),
        # 沪市 B 股
        ("900901", "sh900901"),
        # 深市主板 / 中小板 / 创业板
        ("000001", "sz000001"),
        ("002415", "sz002415"),
        ("300750", "sz300750"),
        # 深市基金 / 债券
        ("159915", "sz159915"),
        ("128035", "sz128035"),
        ("123456", "sz123456"),
        # 深市 B 股
        ("200011", "sz200011"),
        # 北交所：4xxxxx / 8xxxxx / 920xxx
        ("430047", "bj430047"),
        ("830799", "bj830799"),
        ("871981", "bj871981"),
        ("920001", "bj920001"),
    ],
)
def test_normalize_code_infers_market_by_segment(code: str, expected: str) -> None:
    assert normalize_code(code) == expected


def test_five_prefix_is_shanghai_funds() -> None:
    """5xxxxx 必须是沪市，而不是「无法推断」。"""

    for code in ("510300", "511360", "515180", "518850", "588000"):
        assert normalize_code(code) == "sh" + code


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("sz000001", "sz000001"),
        ("SH600000", "sh600000"),
        ("BJ430047", "bj430047"),
        ("  sz000001  ", "sz000001"),
    ],
)
def test_normalize_code_accepts_prefixed_form(value: str, expected: str) -> None:
    assert normalize_code(value) == expected


@pytest.mark.parametrize("code", ["", "60000", "6000000", "abcdef", "12345a", "700000"])
def test_normalize_code_rejects_invalid(code: str) -> None:
    with pytest.raises(ProtocolError):
        normalize_code(code)


def test_split_code_returns_market_id_market_and_number() -> None:
    assert split_code("600000") == (1, "sh", "600000")
    assert split_code("000001") == (0, "sz", "000001")
    assert split_code("430047") == (2, "bj", "430047")
    assert split_code("510300") == (1, "sh", "510300")


def test_market_aliases_and_ids() -> None:
    assert MARKET_TO_ID == {"sz": 0, "sh": 1, "bj": 2}
    for value in ("sz", "SZ", "0", "sza", "深市"):
        assert normalize_market(value) == "sz"
    for value in ("sh", "SH", "1", "sha", "沪市"):
        assert normalize_market(value) == "sh"
    for value in ("bj", "BJ", "2", "bse", "北交所"):
        assert normalize_market(value) == "bj"
    assert normalize_market(0) == "sz"
    assert market_to_id("sh") == 1


@pytest.mark.parametrize("value", ["xx", 9, ""])
def test_market_rejects_unknown(value: object) -> None:
    with pytest.raises(ProtocolError):
        normalize_market(value)  # type: ignore[arg-type]


def test_market_enum_matches_string_mapping() -> None:
    """``Market`` 枚举（easy_tdx 兼容）必须与 ``MARKET_TO_ID`` 一致，防止漂移。"""

    from eltdx.models import Market

    assert {m.code for m in Market} == set(MARKET_TO_ID)
    for member in Market:
        assert MARKET_TO_ID[member.code] == int(member)
        # 枚举与字符串可互换传给 normalize_market / market_to_id
        assert normalize_market(member) == member.code
        assert market_to_id(member.code) == int(member)
        assert market_to_id(member) == int(member)


@pytest.mark.parametrize('number', ['110076', '113692', '118075'])
def test_convertible_bond_bare_codes_use_shanghai_in_python_and_native(number):
    from eltdx.protocol.commands.codec import build_command_frame
    assert normalize_code(number) == 'sh' + number
    native = build_command_frame(0x0FC5, {'code': number, 'count': 1}, 1)
    assert native.data[0] == 1


@pytest.mark.parametrize('number', ['123288', '127089', '128136'])
def test_convertible_bond_bare_codes_keep_shenzhen(number):
    from eltdx.protocol.commands.codec import build_command_frame
    assert normalize_code(number) == 'sz' + number
    assert build_command_frame(0x0FC5, {'code': number, 'count': 1}, 1).data[0] == 0


def _signed_wire_integer(value):
    magnitude = abs(value)
    result = bytearray([(magnitude & 0x3f) | (0x40 if value < 0 else 0)])
    magnitude >>= 6
    if magnitude:
        result[0] |= 0x80
    while magnitude:
        part = magnitude & 0x7f
        magnitude >>= 7
        result.append(part | (0x80 if magnitude else 0))
    return bytes(result)


@pytest.mark.parametrize('code', ['sh110076', 'sh113692', 'sh118075', 'sz123288', 'sz127089', 'sz128136'])
@pytest.mark.parametrize('command', [0x0FC5, 0x0FC6])
def test_convertible_ticks_keep_milli_precision_wire_volume_and_status(code, command):
    import struct
    from eltdx.protocol.commands.codec import parse_command_response
    from eltdx.protocol.frame import ResponseFrame
    # Hand-built protocol input: a price followed by a negative one-milli delta.
    # Same-minute records must remain distinct; auction quantities stay uninterpreted.
    records = b''.join(
        struct.pack('<H', 9 * 60 + 25) + b''.join(_signed_wire_integer(v) for v in values)
        for values in [(125528, 23, 1, 2, 0), (-1, -23, 1, 8, 0)]
    )
    payload = struct.pack('<H', 2) + (struct.pack('<f', 125.0) if command == 0x0FC6 else b'') + records
    request = {'code': code, 'start': 17, 'count': 2, 'include_raw': True}
    if command == 0x0FC6:
        request['trading_date'] = '2026-10-27'
    frame = ResponseFrame(0, 1, command, len(payload), len(payload), payload, b'')
    page = parse_command_response(command, frame, request)
    assert [t.price for t in page.ticks] == [125.528, 125.527]
    assert [t.price_milli for t in page.ticks] == [125528, 125527]
    assert [t.price_acc_raw for t in page.ticks] == [125528, 125527]
    assert [t.volume for t in page.ticks] == [23, -23]
    assert [t.absolute_index for t in page.ticks] == [17, 18]
    assert page.ticks[0].is_opening_match and page.ticks[1].is_auction_snapshot
    assert page.ticks[1].auction_matched_volume is None
    assert page.raw_payload == payload


def test_convertible_trade_price_delta_property():
    """Adversarial wire deltas: no rounding away a one-milli movement."""
    import struct
    from hypothesis import given, settings, strategies as st
    from eltdx.protocol.commands.codec import parse_command_response
    from eltdx.protocol.frame import ResponseFrame

    @settings(max_examples=80, deadline=None, derandomize=True)
    @given(st.sampled_from(['sh110076', 'sh113692', 'sh118075', 'sz123288', 'sz127089', 'sz128136']),
           st.integers(min_value=20, max_value=1_000_000_000),
           st.integers(min_value=-9, max_value=9))
    def check(code, initial, delta):
        records = b''.join(
            struct.pack('<H', 900) + b''.join(_signed_wire_integer(v) for v in [change, 1, 1, 0, 0])
            for change in [initial, delta]
        )
        payload = struct.pack('<H', 2) + records
        frame = ResponseFrame(0, 1, 0x0FC5, len(payload), len(payload), payload, b'')
        page = parse_command_response(0x0FC5, frame, {'code': code, 'count': 2})
        assert [x.price_acc_raw for x in page.ticks] == [initial, initial + delta]
        assert [x.price_milli for x in page.ticks] == [initial, initial + delta]
        assert [x.price for x in page.ticks] == [initial / 1000, (initial + delta) / 1000]
    check()


@pytest.mark.parametrize('code', ['sh110076', 'sh113692', 'sh118075', 'sz123288', 'sz127089', 'sz128136'])
@pytest.mark.parametrize('period', ['day', '1m', '5m'])
def test_convertible_kline_volume_lots_are_bond_lots_not_stock_hundreds(code, period):
    import struct
    from eltdx.protocol.commands.codec import parse_command_response
    from eltdx.protocol.frame import ResponseFrame
    time_bytes = (struct.pack('<I', 20261027) if period == 'day' else
                  struct.pack('<HH', ((2026-2004) << 11) + 1027, 571))
    payload = (struct.pack('<H', 1) + time_bytes +
               b''.join(_signed_wire_integer(v) for v in [125000, 528, 1000, -500]) +
               struct.pack('<II', 0x40000000, 0))
    frame = ResponseFrame(0, 1, 0x052D, len(payload), len(payload), payload, b'')
    request = {'code': code, 'period': period, 'count': 1, 'kind': 'stock', 'include_raw': True}
    series = parse_command_response(0x052D, frame, request)
    bond = series.bars[0]
    assert bond.volume_wire_value == 2 and bond.volume_lots == 2
    assert bond.close == 125.528 and bond.volume_raw == 0x40000000
    assert series.raw_payload == payload and bond.record_hex
    stock = parse_command_response(0x052D, frame, dict(request, code='sz000001')).bars[0]
    assert stock.volume_wire_value == 2 and stock.volume_lots == .02
