"""Live smoke command for the 7615 TQLEX / F10 gateway.

默认跑 A 股核心 5 项；``--extended`` 追加扩展市场家族（美股 / 港股 / 新三板 /
债券 9 类 / 行业 / 期货）与个股总评 / 深度分析新方法；``--macro`` 跑宏观指标
（市场 38，走 ``MacExClient``）。
"""

from __future__ import annotations

import argparse
import threading

from eltdx.f10 import F10Client
from eltdx.f10.client import DEFAULT_MG_HK_BASE_URL

A_SHARE_CODE = "600519"
HK_CODE = "00700"
US_CODE = "NVDA"
SB_CODE = "430047"
BOND_CODE = "113043"
GZ_CODE = "019547"
QYZ_CODE = "122000"
GZHG_CODE = "204001"
INDUSTRY_CODE = "881319"
QH_CODE = "rb"


def _row_counts(response) -> list[int]:
    return [table.count for table in response.tables]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a live smoke check against the 7615 TQLEX / F10 gateway.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--code", default="000034", help="stock code to test")
    parser.add_argument("--timeout", type=float, default=8.0, help="HTTP timeout seconds")
    parser.add_argument(
        "--extended",
        action="store_true",
        help="also check mg/hk/sb/bond/hy/qh families and the stock-analysis methods",
    )
    parser.add_argument(
        "--macro", action="store_true", help="also check macro indicators (market 38, MacExClient)"
    )
    args = parser.parse_args()

    client = F10Client(timeout=args.timeout)
    checks = [
        ("company_profile", client.company_profile(args.code)),
        ("hot_topics", client.hot_topics(args.code)),
        ("announcements", client.announcements(args.code)),
        ("theme_market", client.theme_market(args.code, page_size=-1)),
        ("valuation", client.valuation(args.code)),
    ]

    if args.extended:
        checks.extend(
            [
                # A 股新默认/新方法
                ("finance_diagnosis", client.finance_diagnosis(args.code)),
                ("governance", client.governance(args.code)),
                ("stock_stage_gain", client.stock_stage_gain(args.code)),
                ("stock_main_funds", client.stock_main_funds(args.code)),
                ("stock_industry_rank", client.stock_industry_rank(args.code)),
                ("stock_industry_pct_rank", client.stock_industry_pct_rank(args.code)),
                ("stock_pepb_percentile", client.stock_pepb_percentile(args.code)),
                ("stock_valuation_percentile", client.stock_valuation_percentile(args.code)),
                ("stock_history_trend", client.stock_history_trend(args.code)),
                # 美股
                ("mg_name", client.mg_name(US_CODE)),
                ("mg_profile", client.mg_profile(US_CODE)),
                ("mg_finance", client.mg_finance(US_CODE)),
                ("mg_announcements", client.mg_announcements(US_CODE)),
                # 港股
                ("hk_name", client.hk_name(HK_CODE)),
                ("hk_finance", client.hk_finance(HK_CODE)),
                ("hk_market", client.hk_market(HK_CODE)),
                ("hk_capital_flow", client.hk_capital_flow(HK_CODE)),
                ("hk_analyst_forecast", client.hk_analyst_forecast(HK_CODE)),
                # 新三板
                ("sb_name", client.sb_name(SB_CODE)),
                ("sb_finance", client.sb_finance(SB_CODE)),
                # 债券 9 类
                ("bond_profile", client.bond_profile(BOND_CODE)),
                ("bond_finance", client.bond_finance(BOND_CODE)),
                ("bond_terms", client.bond_terms(BOND_CODE, "hstk")),
                ("gz_profile", client.gz_profile(GZ_CODE)),
                ("gz_interest", client.gz_interest(GZ_CODE)),
                ("qyz_profile", client.qyz_profile(QYZ_CODE)),
                ("qyz_rating", client.qyz_rating(QYZ_CODE)),
                ("gzhg_info", client.gzhg_info(GZHG_CODE)),
                ("gzhg_quotes", client.gzhg_quotes(GZHG_CODE, "bpzs")),
                ("kjhz_finance", client.kjhz_finance("127045")),
                ("zczq_finance", client.zczq_finance("146001")),
                ("bond_bulletin", client.bond_bulletin(GZ_CODE)),
                # 行业
                ("hy_summary", client.hy_summary(INDUSTRY_CODE, "hqtj")),
                ("hy_members_rank", client.hy_members_rank(INDUSTRY_CODE, "cwzkpm")),
                ("hy_index", client.hy_index(INDUSTRY_CODE)),
                # 期货
                ("qh_position_report", client.qh_position_report(QH_CODE, "cjcc", date="20261020")),
                ("qh_basis_spread", client.qh_basis_spread(QH_CODE, "002")),
            ]
        )

    for name, response in checks:
        if not response.ok:
            raise AssertionError(f"{name} returned ErrorCode={response.error_code}")
        print(f"[OK] {name} tables={len(response.tables)} rows={_row_counts(response)}", flush=True)

    print("[OK] f10 smoke passed", flush=True)

    if args.macro:
        _macro_smoke()

    return 0


def _macro_smoke() -> None:
    """宏观指标 smoke（市场 38，MacExClient 7727）。"""

    from eltdx.ex.mac_client import MacExClient
    from eltdx.mac.enums import Period

    result: dict[str, str] = {}

    def work() -> None:
        try:
            client = MacExClient("116.205.135.205", 7727, 10.0)
            client.connect()
            items = client.macro_indicators()
            quotes = client.macro_quotes(["GDP", "CPI", "PMI", "M2"])
            gdp = client.macro_kline("GDP", Period.YEARLY)
            result["indicators"] = str(len(items))
            result["quotes"] = ",".join(
                f"{q.name}={q.fields['close']:.2f}" for q in quotes
            )
            result["gdp_yearly"] = f"{len(gdp)} bars, latest {gdp[-1].datetime.date()}"
            client.close()
        except Exception as exc:  # noqa: BLE001
            result["error"] = f"{type(exc).__name__}: {exc}"

    thread = threading.Thread(target=work, daemon=True)
    thread.start()
    thread.join(60)
    if thread.is_alive() or "error" in result:
        raise AssertionError(result.get("error", "macro smoke timed out"))
    print(f"[OK] macro indicators={result['indicators']}", flush=True)
    print(f"[OK] macro quotes {result['quotes']}", flush=True)
    print(f"[OK] macro gdp yearly {result['gdp_yearly']}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
