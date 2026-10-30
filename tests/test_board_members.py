# -*- coding: utf-8 -*-
"""``F10Client.board_members`` 按记录去重翻页的单测。

该分区一行 = 一条分红记录（同一证券的中报 / 年报各一行），服务端对同日记录的
翻页次序不稳定。这里用脚本化回放验证：按记录身份去重、保留合法多记录、
``zs`` 记录总数兜底、无新增即停、``max_pages`` 保护。
"""

from __future__ import annotations

from typing import Any

import pytest

from eltdx import F10Client
from eltdx.f10 import parse_tqlex_response

_COLUMNS = ["N001", "N002", "sc", "N003", "N004", "N005", "N006", "N007", "N008"]


def _row(
    code: str,
    plan: str = "10派1元(含税)",
    *,
    name: str = "测试证券",
    sc: int = 1,
    progress: str = "实施方案",
    announce: str = "2026-08-31",
    record: str = "2026-09-16",
    ex: str = "2026-09-17",
    period: str = "中报",
) -> dict[str, Any]:
    return {
        "N001": code,
        "N002": name,
        "sc": sc,
        "N003": plan,
        "N004": progress,
        "N005": announce,
        "N006": record,
        "N007": ex,
        "N008": period,
    }


def _response(rows: list[dict[str, Any]], *, total: int | None = None):
    """按 TQLEX 回包形状构造 ``F10Response``（table0 数据 + table1 记录总数）。"""

    content = [[row.get(name) for name in _COLUMNS] for row in rows]
    sets: list[dict[str, Any]] = [
        {
            "Count": len(rows),
            "ResultSetKey": "table0",
            "ColName": list(_COLUMNS),
            "Content": content,
        }
    ]
    if total is not None:
        sets.append(
            {"Count": 1, "ResultSetKey": "table1", "ColName": ["zs"], "Content": [[total]]}
        )
    return parse_tqlex_response(
        "CWServ.skef10_bk_getinfo",
        ["880472", "001", "1", "10"],
        {"ErrorCode": 0, "ResultSets": sets},
    )


def _client(pages: dict[int, list[dict[str, Any]]], *, total: int | None = None):
    """假客户端：``market_report`` 被脚本化，只记录调用。"""

    client = F10Client(timeout=5)
    calls: list[tuple[str, str, int, int]] = []

    def market_report(code, section, *, arg="", date=None, page=1, page_size=20):
        calls.append((code, section, page, page_size))
        return _response(pages.get(page, []), total=total)

    client.market_report = market_report  # type: ignore[method-assign]
    return client, calls


def test_board_members_keeps_distinct_dividend_records_of_one_stock() -> None:
    # 同一证券的中报 / 年报是两条合法记录，都必须保留（不能按代码去重）。
    pages = {
        1: [_row("601236", "10派0.5元(含税)", period="中报"), _row("601236", "10派1.6元(含税)", announce="2026-03-28", period="年报")],
        2: [],
    }
    client, _ = _client(pages, total=2)

    table = client.board_members("880472", page_size=2)

    assert table.count == 2
    assert table.stocks == ("601236",)
    assert [row.report_period for row in table.rows] == ["中报", "年报"]


def test_board_members_dedupes_the_same_record_across_pages() -> None:
    # 服务端页界抖动：page2 重复出现了 page1 已给过的同一条记录。
    pages = {
        1: [_row("601236"), _row("601688", "每10股派1.80元(含税)")],
        2: [_row("601236"), _row("000776", "每10股派2.5元(含税)")],
        3: [],
    }
    client, calls = _client(pages, total=3)

    table = client.board_members("880472", page_size=2)

    assert [row.code for row in table.rows] == ["601236", "601688", "000776"]
    assert table.stocks == ("601236", "601688", "000776")
    # 第 2 页去重后达到 total=3 即停，不会再去要第 3 页。
    assert [page for _, _, page, _ in calls] == [1, 2]


def test_board_members_stops_when_a_page_adds_nothing_new() -> None:
    # 第 2 页整页都是已见记录：服务端页界打滑，应立即停，不空转后续页。
    pages = {
        1: [_row("601236"), _row("601688", "每10股派1.80元(含税)")],
        2: [_row("601236"), _row("601688", "每10股派1.80元(含税)")],
        3: [_row("000776", "每10股派2.5元(含税)")],
    }
    client, calls = _client(pages, total=99)

    table = client.board_members("880472", page_size=2)

    assert table.count == 2
    assert [page for _, _, page, _ in calls] == [1, 2]


def test_board_members_first_page_only_skips_pagination() -> None:
    pages = {1: [_row("601236"), _row("601688", "每10股派1.80元(含税)")], 2: [_row("000776", "每10股派2.5元(含税)")]}
    client, calls = _client(pages, total=99)

    table = client.board_members("880472", all_pages=False, page_size=2)

    assert table.count == 2
    assert [page for _, _, page, _ in calls] == [1]


def test_board_members_respects_max_pages() -> None:
    pages = {index: [_row(f"60000{index}", f"10派0.{index}元(含税)")] for index in range(1, 6)}
    client, calls = _client(pages, total=99)

    table = client.board_members("880472", page_size=1, max_pages=2)

    assert table.count == 2
    assert [page for _, _, page, _ in calls] == [1, 2]


def test_board_members_short_page_ends_pagination() -> None:
    pages = {1: [_row("601236"), _row("601688", "每10股派1.80元(含税)")], 2: [_row("000776", "每10股派2.5元(含税)")]}
    client, calls = _client(pages, total=None)

    table = client.board_members("880472", page_size=2)

    assert table.count == 3
    assert table.total is None
    assert [page for _, _, page, _ in calls] == [1, 2]


def test_board_members_parses_fields_and_derives_full_code() -> None:
    pages = {1: [_row("601236", "10派0.5元(含税)", name="红塔证券", sc=1), _row("000776", "每10股派2.5元(含税)", name="广发证券", sc=0)]}
    client, _ = _client(pages, total=2)

    table = client.board_members("880472", page_size=2)
    first, second = table.rows

    assert (first.code, first.name, first.market_id) == ("601236", "红塔证券", 1)
    assert first.full_code == "sh601236"
    assert first.dividend_plan == "10派0.5元(含税)"
    assert first.progress == "实施方案"
    assert first.announce_date == "2026-08-31"
    assert first.record_date == "2026-09-16"
    assert first.ex_date == "2026-09-17"
    assert first.report_period == "中报"
    assert first.raw["N003"] == "10派0.5元(含税)"
    assert (second.code, second.market_id, second.full_code) == ("000776", 0, "sz000776")


def test_board_members_handles_empty_board() -> None:
    client, calls = _client({}, total=0)

    table = client.board_members("880999")

    assert table.rows == ()
    assert table.total == 0
    assert [page for _, _, page, _ in calls] == [1]


@pytest.mark.parametrize("page_size", [0, -1, 101])
def test_board_members_clamps_page_size(page_size: int) -> None:
    pages = {1: [_row("601236")]}
    client, calls = _client(pages, total=1)

    table = client.board_members("880472", page_size=page_size)

    assert table.count == 1
    # 0 / 负数按 1 处理，101 收敛到服务端上限 100。
    assert calls[0][3] == (1 if page_size <= 0 else 100)
