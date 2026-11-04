"""市场资讯（``tdxi_zxxwsy`` / ``tdxi_zxxwnews``）的离线测试。

三件事分开验：

1. **静态表**：``NewsHomeTab`` / ``NewsChannel`` 的枚举值与中文名映射（含未知值降级）。
2. **请求形状**：``market_news`` / ``channel_news`` 发出的 Entry 与 ``Params`` 顺序。
3. **响应解析**：``extract_news_rows`` 取第 2 个结果集，缺省时返回空列表。

全部离线：``F10Client.call`` 被替身接管，不建立任何 socket。
"""

from __future__ import annotations

import pytest

from eltdx import F10Client
from eltdx.f10.news import (
    HOME_TAB_LABELS,
    NEWS_CHANNEL_LABELS,
    NewsChannel,
    NewsHomeTab,
    channel_name,
    extract_news_rows,
    home_tab_name,
)


class _Captured:
    """记录最近一次 ``call`` 的 Entry 与 body。"""

    def __init__(self) -> None:
        self.entry: str | None = None
        self.body: object | None = None


@pytest.fixture
def f10(monkeypatch):
    cap = _Captured()

    def fake_call(self, entry, body=None, params=None):  # noqa: ANN001 - 替身
        cap.entry = entry
        cap.body = body
        return object()

    monkeypatch.setattr(F10Client, "call", fake_call)
    return F10Client(), cap


# ── 静态表 ────────────────────────────────────────────────────────────────────


def test_home_tab_enum_matches_documented_values() -> None:
    """1 滚动 / 2 今日焦点 / 3 要闻速递 / 4 正面 / 5 负面 / 6 精华 / 7 最新提示 / 9 机构调研。"""

    assert [
        NewsHomeTab.ROLLING,
        NewsHomeTab.TODAY_FOCUS,
        NewsHomeTab.HEADLINES,
        NewsHomeTab.POSITIVE,
        NewsHomeTab.NEGATIVE,
        NewsHomeTab.ESSENCE,
        NewsHomeTab.LATEST_TIPS,
        NewsHomeTab.INSTITUTION_RESEARCH,
    ] == [1, 2, 3, 4, 5, 6, 7, 9]
    assert len(HOME_TAB_LABELS) == 8  # query=8（财经数据）前端已停用，不收录


def test_news_channels_are_sorted_and_cover_every_label() -> None:
    channels = F10Client().news_channels()

    assert channels == sorted(NEWS_CHANNEL_LABELS.items())
    assert len(channels) == len(NEWS_CHANNEL_LABELS) == 84
    assert all(isinstance(cid, int) and isinstance(name, str) for cid, name in channels)


def test_tab_and_channel_names_fall_back_to_the_number() -> None:
    assert home_tab_name(NewsHomeTab.HEADLINES) == HOME_TAB_LABELS[3]
    assert home_tab_name(999) == "999"
    assert channel_name(NewsChannel.FINANCE_HEADLINES) == NEWS_CHANNEL_LABELS[201]
    assert channel_name(9999) == "9999"


# ── 请求形状 ──────────────────────────────────────────────────────────────────


def test_market_news_defaults_to_headlines_first_page(f10) -> None:
    client, cap = f10

    client.market_news()

    assert cap.entry == "CWServ.tdxi_zxxwsy"
    assert cap.body == {"Params": ["3", "1", "50"]}


def test_market_news_forwards_tab_and_paging(f10) -> None:
    client, cap = f10

    client.market_news(NewsHomeTab.TODAY_FOCUS, page=2, page_size=30)

    assert cap.entry == "CWServ.tdxi_zxxwsy"
    assert cap.body == {"Params": ["2", "2", "30"]}


def test_channel_news_forwards_channel_and_paging(f10) -> None:
    client, cap = f10

    client.channel_news(NewsChannel.FINANCE_HEADLINES, page=3, page_size=10, keyword="茅台")

    assert cap.entry == "CWServ.tdxi_zxxwnews"
    # Params 顺序固定为 [query1, 频道号, page, page_size, keyword]
    assert cap.body == {"Params": ["1", "201", "3", "10", "茅台"]}


# ── 响应解析 ──────────────────────────────────────────────────────────────────


class _Table:
    def __init__(self, rows) -> None:
        self.rows = rows


class _Response:
    def __init__(self, tables) -> None:
        self.result_sets = tables


def test_extract_news_rows_reads_the_second_result_set() -> None:
    response = _Response([_Table([{"gate": 1}]), _Table([{"title": "a"}, {"title": "b"}])])

    assert extract_news_rows(response) == [{"title": "a"}, {"title": "b"}]


def test_extract_news_rows_returns_empty_when_the_second_table_is_missing() -> None:
    assert extract_news_rows(_Response([_Table([{"title": "only"}])])) == []


def test_extract_news_rows_tolerates_objects_without_result_sets() -> None:
    assert extract_news_rows(object()) == []
