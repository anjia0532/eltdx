"""宏观指标（市场 38，ExMarket.MACRO_INDICATOR）封装测试。

覆盖重点：
* **防回归**：市场 38 枚举、路由、裸代码补类别逻辑；
* **边界条件**：完整代码/裸代码/歧义代码/未知代码/空输入；
* **缓存行为**：``_macro_code`` 复用 ``macro_indicators`` 缓存，不重复拉列表；
* **不触网**：全部用 mock 替换底层 goods_* 方法。
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from eltdx.ex.enums import ExMarket
from eltdx.ex.mac_client import MacExClient
from eltdx.exceptions import ProtocolError
from eltdx.mac.enums import Period


def _make_client(cache: dict[str, object] | None = None) -> MacExClient:
    """构造一个不联网的 MacExClient（手动装配最小状态）。"""

    client = MacExClient.__new__(MacExClient)
    client._macro_cache = dict(cache or {})
    client._connected = True
    return client


# 模拟 goods_list 返回的指标（name 即代码，如 1_GDP）
_FAKE_INDICATORS = [
    "1_GDP", "1_GDPI", "1_MSR",
    "2_CGPI", "2_CPI", "2_PPCI", "2_PPI", "2_PPPI",
    "3_PMI", "3_PMIN", "3_PMIF",
    "5_M2", "5_XAG", "5_GOLD",
    "8_XAU", "8_ACPI",
    "9_R007", "9_MLF1Y",
]


class _FakeItem:
    """最小 GoodsItem 替身（name 即代码）。"""

    def __init__(self, name: str) -> None:
        self.name = name
        self.category = 10
        self.index = 0


def _fake_items() -> list[_FakeItem]:
    return [_FakeItem(n) for n in _FAKE_INDICATORS]


# ---------------------------------------------------------------------------
# 枚举与常量（防回归）
# ---------------------------------------------------------------------------


def test_macro_market_enum_value() -> None:
    """市场 38 必须是 MACRO_INDICATOR（防枚举值漂移）。"""

    assert ExMarket.MACRO_INDICATOR == 38


def test_macro_categories_mapping() -> None:
    """类别映射覆盖 1~9（对齐通达信宏观数据页分组）。"""

    cats = MacExClient.MACRO_CATEGORIES
    assert set(cats) == {str(i) for i in range(1, 10)}
    assert cats["1"] == "国民经济"
    assert cats["5"] == "货币金融"


# ---------------------------------------------------------------------------
# 代码规范化（_macro_code）
# ---------------------------------------------------------------------------


def test_macro_code_full_form_passthrough() -> None:
    """完整代码（1_GDP）原样通过，不触发列表查询。"""

    client = _make_client()
    assert client._macro_code("1_GDP") == "1_GDP"
    assert client._macro_code(" 2_CPI ") == "2_CPI"


def test_macro_code_bare_code_resolves_unique() -> None:
    """裸代码唯一命中时自动补类别（GDP → 1_GDP）。"""

    items = _fake_items()
    client = _make_client({it.name: it for it in items})
    assert client._macro_code("GDP") == "1_GDP"
    assert client._macro_code("CPI") == "2_CPI"
    assert client._macro_code("R007") == "9_R007"


def test_macro_code_bare_code_ambiguous() -> None:
    """裸代码多类别命中时抛 ValueError 并列出候选。"""

    # 构造一个 XAU 同时在类别 5 与 8 的歧义场景
    names = ["5_XAU", "8_XAU", "1_GDP"]
    client = _make_client({n: MagicMock() for n in names})
    with pytest.raises(ValueError, match="ambiguous"):
        client._macro_code("XAU")


def test_macro_code_bare_code_unknown() -> None:
    """裸代码无命中抛 ProtocolError。"""

    client = _make_client({n: MagicMock() for n in _FAKE_INDICATORS})
    with pytest.raises(ProtocolError, match="unknown macro indicator"):
        client._macro_code("NOTEXIST")


def test_macro_code_empty_cache_fetches_list() -> None:
    """缓存为空时自动拉一次指标列表（且只拉一次）。"""

    client = _make_client()
    client.macro_indicators = MagicMock(  # type: ignore[method-assign]
        side_effect=lambda: [_FakeItem(n) for n in _FAKE_INDICATORS]
    )
    # 第一次：触发列表拉取
    assert client._macro_code("GDP") == "1_GDP"
    assert client.macro_indicators.call_count == 1
    # 第二次：命中缓存，不再拉
    assert client._macro_code("CPI") == "2_CPI"
    assert client.macro_indicators.call_count == 1


# ---------------------------------------------------------------------------
# macro_indicators / macro_quotes / macro_kline（mock 底层）
# ---------------------------------------------------------------------------


def test_macro_indicators_uses_market_38() -> None:
    """macro_indicators 必须查市场 38（防查错市场）。"""

    client = _make_client()
    seen: dict = {}

    def fake_goods_list(market: int, start: int = 0, count: int = 600):
        seen["market"] = market
        seen["calls"] = seen.get("calls", 0) + 1
        return [_FakeItem("1_GDP")]

    client.goods_list = fake_goods_list  # type: ignore[method-assign]
    items = client.macro_indicators()
    assert seen["market"] == 38
    assert len(items) == 1
    # 第二次命中缓存，不再调 goods_list
    client.macro_indicators()
    assert seen.get("calls", 0) == 1


def test_macro_quotes_resolves_codes() -> None:
    """macro_quotes 把裸代码解析成 (38, 1_GDP) 后批量报价。"""

    client = _make_client({n: MagicMock() for n in _FAKE_INDICATORS})
    captured: list = []

    def fake_goods_quotes(stocks, fields=None):
        captured.append(stocks)
        return [MagicMock(code=c) for _, c in stocks]

    client.goods_quotes = fake_goods_quotes  # type: ignore[method-assign]
    result = client.macro_quotes(["GDP", "CPI"])
    assert captured[0] == [(38, "1_GDP"), (38, "2_CPI")]
    assert len(result) == 2


def test_macro_quotes_single_string() -> None:
    """单个字符串代码也接受（不要求包 list）。"""

    client = _make_client({n: MagicMock() for n in _FAKE_INDICATORS})
    captured: list = []
    client.goods_quotes = lambda stocks, fields=None: (captured.append(stocks) or [MagicMock()])  # type: ignore[method-assign]
    client.macro_quotes("GDP")
    assert captured[0] == [(38, "1_GDP")]


def test_macro_kline_default_period_and_market() -> None:
    """macro_kline 默认 MONTHLY、市场 38。"""

    client = _make_client({n: MagicMock() for n in _FAKE_INDICATORS})
    captured: dict = {}

    def fake_goods_kline(market, code, period=Period.DAILY, start=0, count=800, adjust=None):
        captured.update(market=market, code=code, period=period, count=count)
        return [MagicMock()]

    client.goods_kline = fake_goods_kline  # type: ignore[method-assign]
    client.macro_kline("CPI")
    assert captured["market"] == 38
    assert captured["code"] == "2_CPI"
    assert captured["period"] == Period.MONTHLY


def test_macro_kline_yearly_for_gdp() -> None:
    """GDP 年度序列：period=YEARLY 透传。"""

    client = _make_client({n: MagicMock() for n in _FAKE_INDICATORS})
    captured: dict = {}
    client.goods_kline = lambda market, code, period=Period.DAILY, start=0, count=800, adjust=None: (  # type: ignore[method-assign]
        captured.update(period=period) or [MagicMock()]
    )
    client.macro_kline("GDP", Period.YEARLY)
    assert captured["period"] == Period.YEARLY


def test_macro_quotes_empty_list() -> None:
    """空列表不触网、返回空（防无谓请求）。"""

    client = _make_client({n: MagicMock() for n in _FAKE_INDICATORS})
    client.goods_quotes = MagicMock()  # type: ignore[method-assign]
    result = client.macro_quotes([])
    assert result == []
    client.goods_quotes.assert_not_called()
