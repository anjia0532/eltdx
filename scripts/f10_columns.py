"""实测 mg/hk 各 Entry 的返回列名（ColName），输出 tmp_f10/f10_columns.json。

用法: python f10_columns.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from eltdx.f10.client import F10Client


def collect(client: F10Client, name: str, fn, out: dict) -> None:
    try:
        r = fn()
    except Exception as e:  # noqa: BLE001
        out[name] = {"error": f"{type(e).__name__}: {e}", "tables": []}
        return
    tables = []
    for rs in getattr(r, "result_sets", ()) or ():
        cols = list(getattr(rs, "columns", ()) or ())
        tables.append({"key": getattr(rs, "key", ""), "columns": cols})
    out[name] = {"entry": getattr(r, "entry", ""), "tables": tables}


def main() -> None:
    c = F10Client()
    out: dict = {}

    mg = {
        "mg_name": lambda: c.mg_name("NVDA"),
        "mg_tips": lambda: c.mg_tips("NVDA"),
        "mg_profile": lambda: c.mg_profile("NVDA"),
        "mg_finance": lambda: c.mg_finance("NVDA", "zcfzb"),
        "mg_finance_lyb": lambda: c.mg_finance("NVDA", "lyb"),
        "mg_finance_xjllb": lambda: c.mg_finance("NVDA", "xjllb"),
        "mg_finance_indicator": lambda: c.mg_finance_indicator("NVDA", "jbzb"),
        "mg_finance_indicator_yynl": lambda: c.mg_finance_indicator("NVDA", "yynl"),
        "mg_business": lambda: c.mg_business("NVDA"),
        "mg_industry": lambda: c.mg_industry("NVDA"),
        "mg_industry_compare": lambda: c.mg_industry_compare("NVDA"),
        "mg_dividend_fh": lambda: c.mg_dividend("NVDA", "fh"),
        "mg_dividend_cf": lambda: c.mg_dividend("NVDA", "cf"),
        "mg_capital_001": lambda: c.mg_capital("NVDA", "001"),
        "mg_capital_002": lambda: c.mg_capital("NVDA", "002"),
        "mg_shareholders_006": lambda: c.mg_shareholders("NVDA", "006"),
        "mg_shareholders_003": lambda: c.mg_shareholders("NVDA", "003"),
        "mg_directors_ds": lambda: c.mg_directors("NVDA", "ds"),
        "mg_directors_gg": lambda: c.mg_directors("NVDA", "gg"),
        "mg_market_001": lambda: c.mg_market("NVDA", "001"),
        "mg_market_003": lambda: c.mg_market("NVDA", "003"),
        "mg_announcements": lambda: c.mg_announcements("NVDA"),
        "mg_rating_001": lambda: c.mg_rating("NVDA", "001"),
        "mg_rating_002": lambda: c.mg_rating("NVDA", "002"),
        "mg_topic": lambda: c.mg_topic("NVDA"),
        "mg_deep_analysis_001": lambda: c.mg_deep_analysis("NVDA", "001"),
        "mg_deep_analysis_002": lambda: c.mg_deep_analysis("NVDA", "002"),
    }
    hk = {
        "hk_name": lambda: c.hk_name("00700"),
        "hk_tips": lambda: c.hk_tips("00700", "1"),
        "hk_tips_2": lambda: c.hk_tips("00700", "2"),
        "hk_events": lambda: c.hk_events("00700", "1"),
        "hk_events_2": lambda: c.hk_events("00700", "2"),
        "hk_profile": lambda: c.hk_profile("00700", "1"),
        "hk_profile_2": lambda: c.hk_profile("00700", "2"),
        "hk_related": lambda: c.hk_related("00700", "6"),
        "hk_executives": lambda: c.hk_executives("00700", "1"),
        "hk_capital": lambda: c.hk_capital("00700", "1"),
        "hk_shareholders": lambda: c.hk_shareholders("00700", "1"),
        "hk_finance_zcfzb": lambda: c.hk_finance("00700", "zcfzb"),
        "hk_finance_zhsyb": lambda: c.hk_finance("00700", "zhsyb"),
        "hk_finance_indicator": lambda: c.hk_finance_indicator("00700", "jbzb"),
        "hk_business": lambda: c.hk_business("00700", "1"),
        "hk_industry_compare": lambda: c.hk_industry_compare("00700", "1"),
        "hk_market_1": lambda: c.hk_market("00700", "1"),
        "hk_market_2": lambda: c.hk_market("00700", "2"),
        "hk_news": lambda: c.hk_news("00700", "3"),
        "hk_topic": lambda: c.hk_topic("00700"),
        "hk_pepb_band": lambda: c.hk_pepb_band("00700"),
        "hk_valuation": lambda: c.hk_valuation("00700"),
        "hk_price_chart": lambda: c.hk_price_chart("00700"),
        "hk_analyst_forecast": lambda: c.hk_analyst_forecast("00700"),
    }

    for name, fn in {**{f"mg.{k}": v for k, v in mg.items()}, **{f"hk.{k}": v for k, v in hk.items()}}.items():
        collect(c, name, fn, out)

    out_dir = Path(__file__).resolve().parent.parent / "tmp_f10"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "f10_columns.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for name, data in out.items():
        if data.get("error"):
            print(f"{name:28s} ERROR {data['error'][:60]}")
        else:
            all_cols = [c for t in data["tables"] for c in t["columns"]]
            print(f"{name:28s} {len(data['tables'])}表 {len(all_cols)}列: {all_cols[:8]}")


if __name__ == "__main__":
    main()
