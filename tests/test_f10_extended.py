"""美股/港股/新三板/债券 F10 家族与债券代码推断的测试。

覆盖重点（按用户要求）：
* **防回归**：A 股各板块（主板/双创/北交/新三板）代码推断不变；
* **边界条件**：空/非数字/短码/显式前缀/美股港股代码规范化；
* **分页顺序**：跨页顺序拼接，不前插、不颠倒；
* **分页去重**：服务端重复返回时不累积重复、不死循环；
* **F10 家族**：mg/hk/sb/bond 各方法的 Entry 与 Params 正确（mock，不触网）。
"""

from __future__ import annotations

import dataclasses
from unittest.mock import MagicMock, patch

import pytest

from eltdx.exceptions import ProtocolError
from eltdx.f10.client import F10Client, _hk_code, _us_code
from eltdx.f10.fields import describe_fields
from eltdx.mac.client import MacClient
from eltdx.mac.models import MacQuoteField
from eltdx.protocol.unit import normalize_code

# ---------------------------------------------------------------------------
# normalize_code：A 股回归 + 债券分流 + 边界
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "code,expected",
    [
        ("600519", "sh600519"),   # 沪主板
        ("000001", "sz000001"),   # 深主板
        ("300750", "sz300750"),   # 创业板
        ("688981", "sh688981"),   # 科创板
        ("830799", "bj830799"),   # 北交所
        ("920819", "bj920819"),   # 北交所新号段
        ("430047", "bj430047"),   # 新三板（归北交所市场）
        ("510300", "sh510300"),   # 沪 ETF
        ("159915", "sz159915"),   # 深 ETF
        ("900901", "sh900901"),   # 沪 B 股
        ("200992", "sz200992"),   # 深 B 股
    ],
)
def test_normalize_code_ashare_regression(code: str, expected: str) -> None:
    """A 股各板块代码推断必须保持不变（防回归）。"""

    assert normalize_code(code) == expected


@pytest.mark.parametrize(
    "code,expected_market",
    [
        ("113043", "sh"),  # 沪可转债
        ("110043", "sh"),
        ("019547", "sh"),  # 沪国债
        ("122000", "sh"),  # 沪企业债
        ("124000", "sh"),  # 沪公司债
        ("128043", "sz"),  # 深可转债
        ("123018", "sz"),  # 深可转债
        ("100000", "sz"),  # 深国债
        ("111000", "sz"),  # 深可转债
        ("125000", "sz"),  # 深可转债
    ],
)
def test_normalize_code_bond(code: str, expected_market: str) -> None:
    """债券代码段分流：沪市债券段 → sh，深市债券段 → sz。"""

    assert normalize_code(code).startswith(expected_market)


def test_normalize_code_explicit_prefix_wins() -> None:
    """显式前缀优先，且重叠债券段可用前缀强制指定。"""

    assert normalize_code("sh113043") == "sh113043"
    assert normalize_code("sz128043") == "sz128043"
    # 重叠段（120/122）显式指定深市
    assert normalize_code("sz120001") == "sz120001"
    assert normalize_code("sh120001") == "sh120001"


@pytest.mark.parametrize("bad", ["NVDA", "abc", "12345", "1234567", "", "  "])
def test_normalize_code_invalid(bad: str) -> None:
    """非法代码必须抛 ProtocolError，不能静默返回错误市场。"""

    with pytest.raises(ProtocolError):
        normalize_code(bad)


# ---------------------------------------------------------------------------
# 美股 / 港股 / 新三板代码规范化
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "code,expected",
    [
        ("NVDA", "NVDA"),
        ("nvda", "NVDA"),
        ("us.NVDA", "NVDA"),
        ("74.NVDA", "NVDA"),
        ("BRK-B", "BRK-B"),
    ],
)
def test_us_code(code: str, expected: str) -> None:
    assert _us_code(code) == expected


@pytest.mark.parametrize("bad", ["", "  ", "N VD A", "12 34"])
def test_us_code_invalid(bad: str) -> None:
    with pytest.raises(ProtocolError):
        _us_code(bad)


@pytest.mark.parametrize(
    "code,expected",
    [
        ("00700", "00700"),
        ("700", "00700"),      # 前导零补齐
        ("hk.00700", "00700"),
        ("9988", "09988"),
    ],
)
def test_hk_code(code: str, expected: str) -> None:
    assert _hk_code(code) == expected


def test_hk_code_invalid() -> None:
    with pytest.raises(ProtocolError):
        _hk_code("腾讯")


# ---------------------------------------------------------------------------
# 分页：顺序 + 去重（mock _execute，不触网）
# ---------------------------------------------------------------------------


def _quote(code: str) -> MacQuoteField:
    return MacQuoteField(market=1, code=code, name=code, fields={})


def _client_with(fake_execute) -> MacClient:
    """构造 _execute 由 fake_execute 提供的 MacClient（不触网）。"""

    client = MacClient.__new__(MacClient)
    client._execute = fake_execute  # type: ignore[method-assign]
    return client


def test_pagination_order_and_no_duplicates() -> None:
    """分页跨页顺序拼接（第 1 页在前），且最终无重复、条数精确。

    ``_BOARD_MEMBERS_PAGE_SIZE`` 为 80，故取 count=170 强制跨 3 页。
    """

    total = 170
    seen_starts: list[int] = []

    def fake_execute(cmd):
        start, size = cmd._start, cmd._page_size
        seen_starts.append(start)
        return [_quote(f"{i:06d}") for i in range(start + 1, start + size + 1)]

    client = _client_with(fake_execute)
    result = client.get_stock_quotes_list(0, start=0, count=total)
    codes = [q.code for q in result]
    assert codes == [f"{i:06d}" for i in range(1, total + 1)]   # 顺序不颠倒
    assert len(codes) == len(set(codes))                         # 无重复
    assert len(codes) == total                                   # 条数精确
    assert seen_starts == sorted(seen_starts)                    # offset 单调推进


def test_pagination_server_repeats_same_page_terminates() -> None:
    """服务端忽略 start 一直返回满页时：必须有界终止，不死循环。"""

    same = [_quote(f"{i:06d}") for i in range(1, 81)]  # 满页 80

    def fake_execute(cmd):
        return list(same)

    client = _client_with(fake_execute)
    result = client.get_stock_quotes_list(0, start=0, count=200)
    # 有 fetched 上界，必然终止；不会无限循环
    assert len(result) < 1000


# ---------------------------------------------------------------------------
# F10 家族：Entry / Params 正确性（mock _post，不触网）
# ---------------------------------------------------------------------------


def _spy_client() -> F10Client:
    client = F10Client()
    client._post = MagicMock(return_value=MagicMock())  # type: ignore[method-assign]
    return client


def test_bond_family_entry_params() -> None:
    """可转债 F10：Entry 与 Params 正确。"""

    c = _spy_client()
    c.bond_profile("113043")
    c.bond_finance("113043", "zcfzb")
    c.bond_rating("113043", "pjzst")
    c.bond_conversion("113043", "zgjg")
    c.bond_rate("113043", "zqll")
    c.bond_announcements("113043", "1")
    got = [(call.args[0], call.args[1]) for call in c._post.call_args_list]
    assert got == [
        ("CWServ.skef10_bond_kzz_zqgk", {"Params": ["sdcyrbgq", "113043", ""]}),
        ("CWServ.skef10_bond_kzz_cwfx", {"Params": ["zcfzb", "113043"]}),
        ("CWServ.skef10_bond_kzz_zqpj", {"Params": ["pjzst", "113043"]}),
        ("CWServ.skef10_bond_kzz_zg", {"Params": ["zgjg", "113043"]}),
        ("CWServ.skef10_bond_kzz_zqll", {"Params": ["zqll", "113043"]}),
        ("CWServ.skef10_bond_kzz_zjzx", {"Params": ["113043", "1"]}),
    ]


def test_sb_family_entry_params() -> None:
    """新三板 F10：Params 统一 ``[code, section]``。"""

    c = _spy_client()
    c.sb_name("430047")
    c.sb_finance("430047", "zcfzb")
    c.sb_shareholders("430047", "sdgd")
    got = [(call.args[0], call.args[1]) for call in c._post.call_args_list]
    assert got == [
        ("CWServ.skef10_sb_idreq", {"Params": ["name", "430047"]}),
        ("CWServ.skef10_sb_cwfx", {"Params": ["430047", "zcfzb"]}),
        ("CWServ.skef10_sb_gdyj", {"Params": ["430047", "sdgd"]}),
    ]


def test_mg_hk_family_entry_params() -> None:
    """美股/港股 F10：Params 结构正确。"""

    c = _spy_client()
    c.mg_name("NVDA")
    c.mg_finance("NVDA", "zcfzb")
    c.mg_finance_indicator("NVDA", "jbzb")   # 内部映射 001
    c.hk_name("00700")
    c.hk_finance("00700", "zcfzb")            # 内部映射 2
    got = [(call.args[0], call.args[1]) for call in c._post.call_args_list]
    assert got == [
        ("CWServ.skef10_mg_idreq", {"Params": ["name", "NVDA"]}),
        ("CWServ.skef10_mg_cwfx", {"Params": ["zcfzb", "NVDA"]}),
        ("CWServ.skef10_mg_cwzb", {"Params": ["001", "NVDA"]}),
        ("CWServ.skef10_hk_idreq", {"Params": ["name", "00700"]}),
        ("CWServ.skef10_hk_cwfx", {"Params": ["2", "00700"]}),
    ]


def test_bond_gateway_routes_to_page2() -> None:
    """bond/sb/mg/hk Entry 必须走 page2 网关（含 HitCache）。"""

    c = F10Client()
    assert c.mg_hk_base_url.endswith("page2.tdx.com.cn:7615/TQLEX")


def test_f10_invalid_section_raises() -> None:
    """非法 section 必须显式报错（边界条件）。"""

    c = _spy_client()
    with pytest.raises(ValueError):
        c.mg_tips("NVDA", "not_a_section")
    with pytest.raises(ValueError):
        c.hk_finance("00700", "not_a_section")


# ---------------------------------------------------------------------------
# 字段映射：scope 定位 + 重复列后缀
# ---------------------------------------------------------------------------


def test_field_labels_bond_scope() -> None:
    """债券/新三板字段表按 scope（Params 索引）命中。"""

    labels, unmapped = describe_fields(
        "CWServ.skef10_bond_kzz_zqgk",
        {"Params": ["sdcyrbgq", "113043", ""]},
        ["T001", "T002", "T003"],
    )
    # 未登记的列保留原名（不臆测）
    assert unmapped == ["T001", "T002", "T003"]


def test_describe_fields_duplicate_suffix() -> None:
    """服务端同名列（__2 后缀）必须去重并加序号标注。"""

    labels, unmapped = describe_fields(
        "CWServ.skef10_mg_schq",
        {"Params": ["001", "NVDA", 1, 20]},
        ["N001", "N002", "N002__2", "N002__3"],
    )
    assert labels["N001"] == "日期"
    assert labels["N002"] == "开盘价"
    assert labels["N002__2"] == "开盘价（2）"
    assert labels["N002__3"] == "开盘价（3）"
    assert unmapped == []


def test_describe_fields_unknown_scope_preserved() -> None:
    """未知 scope 返回空映射，调用方保留原名。"""

    labels, unmapped = describe_fields(
        "CWServ.skef10_mg_gsgk",
        {"Params": ["999", "NVDA"]},   # 未登记 scope
        ["f11"],
    )
    assert labels == {}
    assert unmapped == ["f11"]


# ---------------------------------------------------------------------------
# 债券全家族（gz/qyz/gzhg/kjhz/zczq/条款/公告）代码规范化与参数构造
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "code,expected",
    [
        ("113043", "113043"),
        ("019547", "019547"),
        ("122000", "122000"),
        ("sh113043", "113043"),
        ("sz128043", "128043"),
        ("128043", "128043"),
    ],
)
def test_bond_code_accepts_valid(code: str, expected: str) -> None:
    from eltdx.f10.client import _bond_code

    assert _bond_code(code) == expected


@pytest.mark.parametrize("code", ["", "NVDA", "abc", "12345", "1234567", "shNVDA", "  "])
def test_bond_code_rejects_invalid(code: str) -> None:
    """边界：空/字母/5位/7位/带前缀的非数字 → ProtocolError。"""

    from eltdx.f10.client import _bond_code

    with pytest.raises(ProtocolError):
        _bond_code(code)


@pytest.mark.parametrize(
    "code,expected",
    [
        ("sh019547", "1"),   # 显式沪市
        ("sz128043", "0"),   # 显式深市
        ("113043", "1"),     # 重叠段默认沪市
        ("sh113043", "1"),
        ("sz123283", "0"),
    ],
)
def test_bond_sc_market_flag(code: str, expected: str) -> None:
    """sc 市场码：显式前缀优先；重叠段默认沪。"""

    from eltdx.f10.client import _bond_sc

    assert _bond_sc(code) == expected


def _capture_params(monkeypatch) -> tuple[F10Client, list]:
    """构造一个记录 params 调用的 F10Client（不触网）。"""

    client = F10Client.__new__(F10Client)
    seen: list[tuple[str, tuple]] = []
    monkeypatch.setattr(
        client, "params", lambda entry, *params: seen.append((entry, params)) or None
    )
    return client, seen


@pytest.mark.parametrize(
    "method,args,entry,params",
    [
        # 国债
        ("gz_profile", ("019547",), "CWServ.skef10_bond_gz_zjgk", ("zqgk", "019547", "1")),
        ("gz_profile", ("019547", "fxgk"), "CWServ.skef10_bond_gz_zjgk", ("fxgk", "019547", "1")),
        ("gz_interest", ("019547",), "CWServ.skef10_bond_gz_fxqk", ("fxqk", "019547", "1")),
        ("gz_market_data", ("019547",), "CWServ.skef10_bond_gz_zjsj", ("dzjy", "019547", "1")),
        ("gz_rating", ("019547",), "CWServ.skef10_bond_gz_zjpj", ("dfzf", "019547", "1")),
        ("gz_finance", ("019547",), "CWServ.skef10_bond_gz_cwfx", ("t", "019547", "1")),
        # 企业债
        ("qyz_profile", ("122000",), "CWServ.skef10_bond_qyz_zqgk", ("zqzl", "122000", "1")),
        ("qyz_interest", ("122000",), "CWServ.skef10_bond_qyz_xjlfx", ("fxqk", "122000", "1")),
        ("qyz_guarantee", ("122000",), "CWServ.skef10_bond_qyz_zqdb", ("dbsm", "122000", "1")),
        ("qyz_rating", ("122000",), "CWServ.skef10_bond_qyz_zjpj", ("zjpjzst", "122000", "1")),
        ("qyz_rate", ("122000",), "CWServ.skef10_bond_qyz_zjlv", ("zqlv", "122000", "1")),
        ("qyz_review", ("122000",), "CWServ.skef10_bond_qyz_gsps", ("122000", "1")),
        # 国债回购（无 sc）
        ("gzhg_info", ("204001",), "CWServ.skef10_bond_gzhg_zqxx", ("zqgk", "204001")),
        ("gzhg_quotes", ("204001",), "CWServ.skef10_bond_gzhg_zqxx", ("bpzs", "204001")),
        # 可交换债
        ("kjhz_finance", ("127045",), "CWServ.skef10_bond_kjhz_cwfx", ("t", "127045")),
        ("kjhz_exchange", ("127045",), "CWServ.skef10_bond_kjhz_jhqk", ("jgtzzst", "127045")),
        ("kjhz_rate", ("127045",), "CWServ.skef10_bond_kjhz_zqll", ("zqll", "127045")),
        # ABS
        ("zczq_finance", ("146001",), "CWServ.skef10_bond_zczqh_cwfx", ("t", "146001", "1")),
        # 通用条款/公告
        ("bond_terms", ("113043",), "CWServ.skef10_bond_kzz_lltk", ("hstk", "113043")),
        ("bond_bulletin", ("019547",), "CWServ.skef10_bond_zjzx", ("019547", "1")),
    ],
)
def test_bond_family_params(
    monkeypatch, method: str, args: tuple, entry: str, params: tuple
) -> None:
    """债券各家族的 Entry 与 Params 拼装（mock，防参数错位回归）。"""

    client, seen = _capture_params(monkeypatch)
    getattr(client, method)(*args)
    assert seen == [(entry, params)]


def test_bond_family_sc_suffix(monkeypatch) -> None:
    """显式 sz 前缀时 sc 必须为 '0'（防市场码错位）。"""

    client, seen = _capture_params(monkeypatch)
    client.gz_profile("sz019547")
    assert seen[0][1][2] == "0"


# ---------------------------------------------------------------------------
# 行业 hyf10 家族
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method,args,entry,params",
    [
        ("hy_summary", ("881319",), "CWServ.skef10_hy_hqtj", ("881319",)),
        ("hy_summary", ("881319", "hyzq"), "CWServ.skef10_hy_hyzq", ("881319",)),
        ("hy_summary", ("881319", "zszfb"), "CWServ.skef10_hy_zszfb", ("881319",)),
        ("hy_stage_rise", ("881319",), "CWServ.skef10_hy_jdzf", ("881319", "e")),
        ("hy_profile", ("881319",), "CWServ.skef10_hy_hyzl_hyjs", ("881319",)),
        ("hy_commentary", ("881319",), "CWServ.skef10_hy_hyzl_hyplk", ("001", "881319")),
        ("hy_news", ("881319",), "CWServ.skef10_hy_zxdt", ("hydt", "881319")),
        ("hy_news", ("881319", "hyzt"), "CWServ.skef10_hy_zxdt", ("hyzt", "881319")),
        ("hy_members_rank", ("881319", "cwzkpm"), "CWServ.skef10_hy_hydw_cwzkpm",
         ("002", "881319", "", "e", "")),
        ("hy_members_rank", ("881319", "gsgmpm"), "CWServ.skef10_hy_hydw_gsgmpm", ("881319",)),
        ("hy_members_rank", ("881319", "gzsppm"), "CWServ.skef10_hy_hydw_gzsppm", ("01", "881319", "o")),
        ("hy_members_rank", ("881319", "scbxpm"), "CWServ.skef10_hy_hydw_scbxpm", ("scpm", "", "881319")),
        ("hy_members_rank", ("881319", "zysrpm"), "CWServ.skef10_hy_hydw_zysrpm", ("001", "881319", "")),
        ("hy_capital_stats", ("881319",), "CWServ.skef10_hy_hysj_bxzjtj", ("001", "881319", "n")),
        ("hy_fund_holdings", ("881319",), "CWServ.skef10_hy_hysj_jjzb", ("1", "881319", "")),
        ("hy_capital_flow", ("881319",), "CWServ.skef10_hy_hysj_zjlx", ("001", "881319")),
        ("hy_analyst_index", ("881319",), "CWServ.skef10_hy_hyyj_fxszs", ("001", "881319", "", "")),
        ("hy_major_holders", ("881319",), "CWServ.skef10_hy_hyyj_hymzgd", ("881319",)),
        ("hy_rating_summary", ("881319",), "CWServ.skef10_hy_hyyj_hypjhz", ("001", "881319", "")),
        ("hy_index", ("881319",), "CWServ.skef10_hy_idsy", ("002", "881319")),
    ],
)
def test_hy_family_params(
    monkeypatch, method: str, args: tuple, entry: str, params: tuple
) -> None:
    """行业各方法的 Entry 与 Params 拼装（mock）。"""

    client, seen = _capture_params(monkeypatch)
    getattr(client, method)(*args)
    assert seen == [(entry, params)]


def test_hy_members_rank_unknown_section(monkeypatch) -> None:
    """未知 section 必须抛 ValueError（防静默走错 Entry）。"""

    client, _ = _capture_params(monkeypatch)
    with pytest.raises(ValueError):
        client.hy_members_rank("881319", "not_exist")


def test_hy_summary_unknown_section(monkeypatch) -> None:
    """hy_summary 未知 section 抛 KeyError/ValueError，不静默。"""

    client, _ = _capture_params(monkeypatch)
    with pytest.raises(Exception):
        client.hy_summary("881319", "not_exist")


# ---------------------------------------------------------------------------
# 期货 qhf10 家族
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method,kwargs,entry,params",
    [
        ("qh_position_report", {"section": "cjcc", "date": "20261020"},
         "CWServ.qhf9_sp_ccbg_cjcc", ("1", "rb", "20261020")),
        ("qh_position_report", {"section": "cjjg", "date": "20261020"},
         "CWServ.qhf9_sp_ccbg_cjjg", ("1", "rb", "20261020", "")),
        ("qh_position_report", {"section": "jcgc", "date": "20261001", "end_date": "20261020"},
         "CWServ.qhf9_sp_ccbg_jcgc", ("1", "rb", "20261001", "20261020", "")),
        ("qh_position_report", {"section": "cjcc", "date": "20261020", "index": True},
         "CWServ.qhf9_gz_ccbg_cjcc", ("1", "IF", "20261020")),
        ("qh_basis_spread", {"section": "002"},
         "CWServ.qhf9_sp_jcjcfx", ("002", "rb", "1Y", "", "")),
        ("qh_warehouse_receipt", {"date": "20261020"},
         "CWServ.qhf9_sp_ckrb_ckrb", ("1", "rb", "20261020")),
        ("qh_inventory", {}, "CWServ.qhf9_sp_kcbg_kcbg", ("1", "rb")),
        ("qh_variety_info", {"section": "pzjj"},
         "CWServ.qhf9_sp_pzzl_pzjj", ("rb", "1")),
        ("qh_variety_info", {"section": "hyjj"},
         "CWServ.qhf9_sp_pzzl_hyjj", ("rb",)),
        ("qh_variety_info", {"section": "xgzq"},
         "CWServ.qhf9_sp_pzzl_xgzq", ("rb",)),
        ("qh_index_info", {"section": "zsgk"},
         "CWServ.qhf9_gz_zszl_zsgk", ("1", "399300")),
        ("qh_index_info", {"section": "lsjg"},
         "CWServ.qhf9_gz_zszl_lsjg", ("2", "399300")),
        ("qh_index_valuation", {"section": "dtpe", "start": "20251020", "end": "20261020"},
         "CWServ.qhf9_gz_zsgz_dtpe", ("1", "000300", "20251020", "20261020")),
        ("qh_weights", {"section": "zxcfg"},
         "CWServ.qhf9_gz_cfg_zxcfg", ("1", "399300", "")),
        ("qh_weights", {"section": "cfghyfb"},
         "CWServ.qhf9_gz_cfg_cfghyfb", ("1", "399300")),
    ],
)
def test_qh_family_params(
    monkeypatch, method: str, kwargs: dict, entry: str, params: tuple
) -> None:
    """期货各方法的 Entry 与 Params 拼装（mock）。"""

    client, seen = _capture_params(monkeypatch)
    # 指数类方法的 code 是指数代码，其余是品种代码
    code = "IF" if kwargs.get("index") else ("399300" if method in ("qh_index_info", "qh_weights") else "rb")
    if method == "qh_index_valuation":
        code = "000300"
    getattr(client, method)(code, **kwargs)
    assert seen == [(entry, params)]


def test_qh_date_normalization(monkeypatch) -> None:
    """日期带 ``-`` 时必须去掉（与客户端一致）。"""

    client, seen = _capture_params(monkeypatch)
    client.qh_position_report("rb", "cjcc", date="2026-10-20")
    assert seen[0][1][2] == "20261020"
    client.qh_warehouse_receipt("rb", date="2026-10-20")
    assert seen[0][1][2] == "20261020"


def test_qh_position_report_unknown_section(monkeypatch) -> None:
    """持仓报告未知 section 抛 KeyError（不静默走错）。"""

    client, _ = _capture_params(monkeypatch)
    with pytest.raises(KeyError):
        client.qh_position_report("rb", "not_exist", date="20261020")


def test_mg_hk_entry_gateway_routing() -> None:
    """网关路由：qhf9 Entry 必须命中 page2（防缓存失效回归）。"""

    from eltdx.f10.client import _QH_ENTRY_PREFIXES, _MG_HK_ENTRY_PREFIXES

    assert "CWServ.qhf9_sp_ccbg_cjcc".startswith(_QH_ENTRY_PREFIXES)
    assert "CWServ.skef10_hy_hqtj".startswith(_MG_HK_ENTRY_PREFIXES)
    assert "CWServ.skef10_bond_gz_zjgk".startswith(_MG_HK_ENTRY_PREFIXES)
    assert not "CWServ.tdxf10_gg_comreq".startswith(_QH_ENTRY_PREFIXES)


def test_bond_code_no_market_inference_collision() -> None:
    """沪深重叠段（110/113/120/122/124）不纯代码段推断，避免错分市场。"""

    from eltdx.f10.client import _bond_code, _bond_sc

    # 110043 沪市可转债 vs 深市重叠段：不抛错、默认沪
    assert _bond_code("110043") == "110043"
    assert _bond_sc("110043") == "1"
    # 深市必须显式前缀才能得到 0
    assert _bond_sc("sz110043") == "0"


# ---------------------------------------------------------------------------
# 各行业龙头矩阵实测发现的默认值/遗漏修复（2026-10-22）
# ---------------------------------------------------------------------------


def test_finance_diagnosis_default_section_zzyj(monkeypatch) -> None:
    """回归：finance_diagnosis 默认 zzyj（yynl 已随页面改版下线）。"""

    client, seen = _capture_params(monkeypatch)
    client.finance_diagnosis("600519")
    assert seen[0] == ("CWServ.tdxf10_gg_cwzd", ("zzyj", "600519", ""))


def test_governance_default_section_gljy(monkeypatch) -> None:
    """回归：governance 默认 gljy（现行页面 5 section 中数据最全）。"""

    client, seen = _capture_params(monkeypatch)
    client.governance("600519")
    assert seen[0] == ("CWServ.tdxf10_gg_zbyz", ("gljy", "600519", ""))


def test_hk_market_default_section(monkeypatch) -> None:
    """回归：hk_market 默认 3（1/2/5 对腾讯实测空）。"""

    client, seen = _capture_params(monkeypatch)
    client.hk_market("00700")
    assert seen[0] == ("CWServ.skef10_hk_schq", ("3", "00700"))


def test_hk_capital_flow(monkeypatch) -> None:
    """hk_capital_flow（skef10_hk_schq_zjlx，龙头矩阵发现未封装）。"""

    client, seen = _capture_params(monkeypatch)
    client.hk_capital_flow("00700")
    assert seen[0] == ("CWServ.skef10_hk_schq_zjlx", ("001", "00700", "0"))


def test_hk_analyst_forecast_defaults_to_last_year(monkeypatch) -> None:
    """回归：hk_analyst_forecast 空日期时默认近一年（实测空日期 0 行）。"""

    client, seen = _capture_params(monkeypatch)
    client.hk_analyst_forecast("00700")
    entry, params = seen[0]
    assert entry == "CWServ.skef10_hk_sdfx_fxysyfx"
    assert params[0] == "00700"
    # 起止均为 8 位数字日期
    assert len(params[1]) == 8 and params[1].isdigit()
    assert len(params[2]) == 8 and params[2].isdigit()
    assert params[1] < params[2]


def test_hk_analyst_forecast_explicit_dates(monkeypatch) -> None:
    """显式日期仍按原语义（去横线）。"""

    client, seen = _capture_params(monkeypatch)
    client.hk_analyst_forecast("00700", "2024-10-22", "2026-10-22")
    assert seen[0][1] == ("00700", "20241022", "20261022")
