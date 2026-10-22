"""个股总评（ggzp）/ 深度分析（sdfx）新封装方法的测试。

覆盖 2026-10-22 从客户端 F10 缓存审计发现的遗漏：
* ``stock_stage_gain`` / ``stock_main_funds`` / ``stock_industry_rank`` /
  ``stock_industry_pct_rank`` / ``stock_board_member_quotes``
  （``HQServ.hq_nlp_tcihq`` ReqId 200740/200742/200744/200745/200747）
* ``stock_valuation_percentile`` / ``stock_pepb_percentile`` /
  ``stock_history_trend``（``HQServ.hq_nlp_gpsj`` ReqId 200192/200124/200135）
* ``stock_finance_weights``（``CWServ.tdxf10_gg_zxtscwbq``）

全部 mock，不触网；重点防 **200740 漏 zq_num** 的回归（该 bug 曾导致
日线序列 t1 返回 0 行）。
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from eltdx.f10.client import F10Client


def _capture(monkeypatch) -> tuple[F10Client, list]:
    client = F10Client.__new__(F10Client)
    seen: list[tuple[str, object]] = []
    monkeypatch.setattr(
        client,
        "call",
        lambda entry, body: (seen.append((entry, body)) or MagicMock()),
    )
    return client, seen


def _reqid(body: object) -> str:
    return str(body[0]["ReqId"])  # type: ignore[index]


def _payload(body: object) -> dict:
    return body[0]  # type: ignore[index]


# ---------------------------------------------------------------------------
# tcihq 家族（个股总评）
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method,kwargs,expected_reqid,expected_zq_num",
    [
        ("stock_stage_gain", {}, "200740", "60"),
        ("stock_stage_gain", {"days": 120}, "200740", "120"),
        ("stock_main_funds", {}, "200742", "30"),
        ("stock_industry_rank", {}, "200745", "30"),
        ("stock_industry_pct_rank", {}, "200747", "30"),
        ("stock_industry_pct_rank", {"days": 60}, "200747", "60"),
    ],
)
def test_tcihq_methods_send_zq_num(
    monkeypatch, method: str, kwargs: dict, expected_reqid: str, expected_zq_num: str
) -> None:
    """tcihq 方法必须带 zq_num（200740 曾漏掉导致 t1 空）。"""

    client, seen = _capture(monkeypatch)
    getattr(client, method)("601318", **kwargs)
    entry, body = seen[0]
    assert entry == "HQServ.hq_nlp_tcihq"
    assert _reqid(body) == expected_reqid
    assert _payload(body)["zq_num"] == expected_zq_num
    assert _payload(body)["code"] == "601318"
    assert _payload(body)["setcode"] == 1


def test_stock_stage_gain_regression_zq_num(monkeypatch) -> None:
    """回归：200740 必须携带 zq_num，否则服务端只返回 t0 统计行。

    2026-10-22 实测：漏 zq_num 时 t1（日线序列）为 0 行，带上后 60 行。
    """

    client, seen = _capture(monkeypatch)
    client.stock_stage_gain("601318")
    payload = _payload(seen[0][1])
    assert "zq_num" in payload, "200740 漏 zq_num 回归"
    assert payload["zq_num"] == "60"


def test_stock_board_member_quotes_params(monkeypatch) -> None:
    """200744 关联板块成分：板块代码在前、Page=-1/PageSize=-1。"""

    client, seen = _capture(monkeypatch)
    client.stock_board_member_quotes("881001")
    entry, body = seen[0]
    assert entry == "HQServ.hq_nlp_tcihq"
    assert _reqid(body) == "200744"
    assert _payload(body)["code"] == "881001"
    assert _payload(body)["setcode"] == "1"
    assert _payload(body)["Page"] == -1
    assert _payload(body)["PageSize"] == "-1"


def test_stock_board_member_quotes_market(monkeypatch) -> None:
    """可指定板块市场（board_market=0 深市）。"""

    client, seen = _capture(monkeypatch)
    client.stock_board_member_quotes("881001", board_market=0)
    assert _payload(seen[0][1])["setcode"] == "0"


# ---------------------------------------------------------------------------
# gpsj 家族（深度分析估值）
# ---------------------------------------------------------------------------


def test_stock_valuation_percentile_kind(monkeypatch) -> None:
    """200192 估值分位：Type 透传（0=PE / 1=PB）。"""

    for kind, expect in [("0", "0"), ("1", "1"), ("2", "2"), ("3", "3")]:
        client, seen = _capture(monkeypatch)
        client.stock_valuation_percentile("601318", kind)
        entry, body = seen[0]
        assert entry == "HQServ.hq_nlp_gpsj"
        assert _reqid(body) == "200192"
        assert _payload(body)["Type"] == expect
        assert _payload(body)["Code"] == "601318|1"


def test_stock_pepb_percentile_params(monkeypatch) -> None:
    """200124：zb 指标 / sjfw 窗口 / hqzq 周期透传。"""

    client, seen = _capture(monkeypatch)
    client.stock_pepb_percentile("601318", "1", window="3Y", period="2")
    payload = _payload(seen[0][1])
    assert _reqid(seen[0][1]) == "200124"
    assert payload["zb"] == "1"
    assert payload["sjfw"] == "3Y"
    assert payload["hqzq"] == "2"


def test_stock_history_trend(monkeypatch) -> None:
    """200135 年度历史走势。"""

    client, seen = _capture(monkeypatch)
    client.stock_history_trend("601318")
    entry, body = seen[0]
    assert entry == "HQServ.hq_nlp_gpsj"
    assert _reqid(body) == "200135"


# ---------------------------------------------------------------------------
# zxtscwbq（财务指标权重）
# ---------------------------------------------------------------------------


def test_stock_finance_weights(monkeypatch) -> None:
    """zxtscwbq：Params 为 [code, section]。"""

    client = F10Client.__new__(F10Client)
    seen: list[tuple[str, tuple]] = []
    monkeypatch.setattr(
        client, "params", lambda entry, *p: (seen.append((entry, p)) or MagicMock())
    )
    client.stock_finance_weights("601318", "zcfzb")
    assert seen == [("CWServ.tdxf10_gg_zxtscwbq", ("601318", "zcfzb"))]


# ---------------------------------------------------------------------------
# 与底层方法的对应关系（防改串）
# ---------------------------------------------------------------------------


def test_methods_delegate_to_theme_market(monkeypatch) -> None:
    """四个 tcihq 语义方法都走 theme_market（单一构造点）。"""

    client = F10Client.__new__(F10Client)
    calls: list[tuple] = []
    monkeypatch.setattr(
        client,
        "theme_market",
        lambda code, req_id, **kw: calls.append((code, req_id, kw)) or MagicMock(),
    )
    client.stock_stage_gain("600519", days=90)
    client.stock_main_funds("600519", days=15)
    client.stock_industry_rank("600519", days=7)
    client.stock_industry_pct_rank("600519", days=7)
    assert [str(c[1]) for c in calls] == ["200740", "200742", "200745", "200747"]
    assert all(c[2].get("zq_num") for c in calls)


def test_methods_delegate_to_valuation(monkeypatch) -> None:
    """三个 gpsj 语义方法都走 valuation。"""

    client = F10Client.__new__(F10Client)
    calls: list[tuple] = []
    monkeypatch.setattr(
        client,
        "valuation",
        lambda code, req_id, **kw: calls.append((code, req_id, kw)) or MagicMock(),
    )
    client.stock_valuation_percentile("600519", "1")
    client.stock_pepb_percentile("600519", "2", window="5Y")
    client.stock_history_trend("600519")
    assert [str(c[1]) for c in calls] == ["200192", "200124", "200135"]
