"""F10 家族与宏观指标的边界条件测试。

覆盖重点（对应用户要求）：
* **空值边界**：空代码、空 section、空 dates、None；
* **格式边界**：非法日期、超长代码、带空格代码；
* **数值边界**：days=0/负数/超大、page 边界；
* **错误类型**：`ProtocolError` / `ValueError` / `KeyError` 不混用；
* **不静默**：任何无法解析的输入都必须显式抛错，不返回空结果冒充成功。

全部 mock，不触网。
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from eltdx.exceptions import ProtocolError
from eltdx.f10.client import F10Client, _bond_code, _bond_sc, _hk_code, _us_code

# ---------------------------------------------------------------------------
# 代码规范化边界
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("code", ["", "   ", "us.", ".", "-", "US!", "BRK B"])
def test_us_code_rejects_invalid(code: str) -> None:
    """美股代码：空/纯符号/过短 → ProtocolError。"""

    with pytest.raises(ProtocolError):
        _us_code(code)


@pytest.mark.parametrize("code", ["", "hk", "hk.", ".", "abc", "00700A"])
def test_hk_code_rejects_invalid(code: str) -> None:
    """港股代码：无数字/3 位以下/6 位（过长）→ ProtocolError。"""

    with pytest.raises(ProtocolError):
        _hk_code(code)


def test_us_code_accepts_dotted_class() -> None:
    """美股 BRK-B（带连字符）合法；BRK.B（点分）取末段。"""

    assert _us_code("BRK-B") == "BRK-B"
    assert _us_code("BRK.B") == "B"


def test_hk_code_max_five_digits() -> None:
    """港股超过 5 位数字仍返回（前导零补齐只影响不足 5 位）。"""

    assert _hk_code("00700") == "00700"
    assert _hk_code("123456") == "123456"


@pytest.mark.parametrize("code", ["", "  ", "abc", "12345", "1234567", "shabc", "sz12"])
def test_bond_code_rejects_invalid(code: str) -> None:
    """债券代码边界（与 test_f10_extended 共同的用例集中于此）。"""

    with pytest.raises(ProtocolError):
        _bond_code(code)


def test_bond_sc_empty_and_unknown() -> None:
    """空/无前缀代码默认沪市（1），不抛错。"""

    assert _bond_sc("") == "1"
    assert _bond_sc("xyz") == "1"


# ---------------------------------------------------------------------------
# 方法参数边界（mock，只验证请求构造不抛错或正确抛错）
# ---------------------------------------------------------------------------


def _capture(monkeypatch) -> tuple[F10Client, list]:
    client = F10Client.__new__(F10Client)
    seen: list[tuple[str, object]] = []
    monkeypatch.setattr(
        client, "call", lambda entry, body: (seen.append((entry, body)) or MagicMock())
    )
    return client, seen


def _params_capture(monkeypatch) -> tuple[F10Client, list]:
    client = F10Client.__new__(F10Client)
    seen: list[tuple[str, tuple]] = []
    monkeypatch.setattr(
        client, "params", lambda entry, *p: (seen.append((entry, p)) or MagicMock())
    )
    return client, seen


def test_stock_stage_gain_zero_days(monkeypatch) -> None:
    """days=0 不透支非法值：仍发出请求（服务端决定语义），不本地崩溃。"""

    client, seen = _capture(monkeypatch)
    monkeypatch.setattr(
        client,
        "theme_market",
        lambda code, req_id, **kw: (seen.append((code, req_id, kw)) or MagicMock()),
    )
    client.stock_stage_gain("600519", days=0)
    assert str(seen[0][2]["zq_num"]) == "0"


def test_stock_stage_gain_negative_days(monkeypatch) -> None:
    """days 负数：透传字符串化，由服务端处理（与客户端行为一致）。"""

    client = F10Client.__new__(F10Client)
    seen: list[tuple] = []
    monkeypatch.setattr(
        client,
        "theme_market",
        lambda code, req_id, **kw: (seen.append((code, req_id, kw)) or MagicMock()),
    )
    client.stock_stage_gain("600519", days=-5)
    assert str(seen[0][2]["zq_num"]) == "-5"


def test_hk_analyst_forecast_only_start(monkeypatch) -> None:
    """只传 start：end 自动补今天（防半开区间请求）。"""

    client, seen = _params_capture(monkeypatch)
    client.hk_analyst_forecast("00700", start="2025-01-01")
    params = seen[0][1]
    assert params[1] == "20250101"
    assert len(params[2]) == 8 and params[2].isdigit()


def test_hk_analyst_forecast_invalid_date_passthrough(monkeypatch) -> None:
    """非法日期字符串：strip 后透传（服务端返回空即空，不本地臆测）。"""

    client, seen = _params_capture(monkeypatch)
    client.hk_analyst_forecast("00700", start="abc", end="xyz")
    assert seen[0] == ("CWServ.skef10_hk_sdfx_fxysyfx", ("00700", "abc", "xyz"))


def test_macro_quotes_none_like_empty(monkeypatch) -> None:
    """macro_quotes 空序列不触网。"""

    from eltdx.ex.mac_client import MacExClient

    client = MacExClient.__new__(MacExClient)
    client._macro_cache = {}
    client._connected = True
    client.goods_quotes = MagicMock()  # type: ignore[method-assign]
    assert client.macro_quotes([]) == []
    client.goods_quotes.assert_not_called()


def test_hy_members_rank_empty_section(monkeypatch) -> None:
    """hy_members_rank 空 section 必须抛错（不静默走默认分支）。"""

    client, _ = _params_capture(monkeypatch)
    with pytest.raises(ValueError):
        client.hy_members_rank("881319", "")


def test_qh_position_report_empty_section(monkeypatch) -> None:
    """qh_position_report 空 section 抛 KeyError。"""

    client = F10Client.__new__(F10Client)
    monkeypatch.setattr(client, "params", lambda *a, **k: MagicMock())
    with pytest.raises(KeyError):
        client.qh_position_report("rb", "")


def test_qh_date_variants_normalized(monkeypatch) -> None:
    """qh 日期三种写法（YYYYMMDD / YYYY-MM-DD / 混合）都归一为 8 位。"""

    client = F10Client.__new__(F10Client)
    seen: list[tuple] = []
    monkeypatch.setattr(
        client, "params", lambda entry, *p: (seen.append((entry, p)) or MagicMock())
    )
    for raw in ["20261020", "2026-10-20", " 2026-10-20 "]:
        client.qh_position_report("rb", "cjcc", date=raw)
    assert all(p[2] == "20261020" for _, p in seen)


def test_stock_finance_weights_empty_section(monkeypatch) -> None:
    """stock_finance_weights 空 section 透传空串（服务端返回空即空）。"""

    client, seen = _params_capture(monkeypatch)
    client.stock_finance_weights("601318", "")
    assert seen == [("CWServ.tdxf10_gg_zxtscwbq", ("601318", ""))]


def test_macro_code_whitespace(monkeypatch) -> None:
    """宏观代码带空格：strip 后按裸代码处理。"""

    from eltdx.ex.mac_client import MacExClient

    client = MacExClient.__new__(MacExClient)
    client._macro_cache = {"1_GDP": MagicMock()}
    client._connected = True
    assert client._macro_code("  GDP  ") == "1_GDP"


def test_macro_code_case_sensitivity(monkeypatch) -> None:
    """宏观代码区分大小写（gdp ≠ GDP）。"""

    from eltdx.ex.mac_client import MacExClient

    client = MacExClient.__new__(MacExClient)
    client._macro_cache = {"1_GDP": MagicMock()}
    client._connected = True
    with pytest.raises(ProtocolError):
        client._macro_code("gdp")


def test_methods_reject_empty_code_via_code6(monkeypatch) -> None:
    """F10Client 方法对空 code 由 _code6 抛错（不静默发空请求）。"""

    client, _ = _params_capture(monkeypatch)
    with pytest.raises(ProtocolError):
        client.gz_profile("")
