"""各行业龙头全 F10 方法矩阵实测，找失败/异常空的项。"""
from __future__ import annotations

import sys
import threading
import traceback
from pathlib import Path

sys.path.insert(0, str(Path("D:/AnJia/Work/workspace/python/eltdx/src").resolve()))

from eltdx.f10.client import F10Client  # noqa: E402

# 各行业龙头（覆盖 4 种 nhytype + 各板块 + 北交所/新三板/港股/美股）
LEADERS = [
    ("600519", "贵州茅台", "消费"),
    ("601398", "工商银行", "银行"),
    ("600030", "中信证券", "券商"),
    ("601318", "中国平安", "保险"),
    ("688981", "中芯国际", "科创"),
    ("300750", "宁德时代", "创业板"),
    ("000002", "万科A", "房地产"),
    ("601899", "紫金矿业", "有色"),
    ("600019", "宝钢股份", "钢铁"),
    ("601088", "中国神华", "煤炭"),
    ("600900", "长江电力", "电力"),
    ("000333", "美的集团", "家电"),
    ("600276", "恒瑞医药", "医药"),
    ("601766", "中国中车", "机械"),
    ("600028", "中国石化", "石化"),
    ("000876", "新希望", "农业"),
    ("002415", "海康威视", "电子"),
    ("601006", "大秦铁路", "交运"),
    ("830799", "艾融软件", "北交所"),
    ("430047", "诺思兰德", "新三板"),
]

# (方法名, 调用工厂)
ASHARE_METHODS = [
    ("stock_info", lambda c, k: c.stock_info(k)),
    ("company_profile", lambda c, k: c.company_profile(k)),
    ("finance_report zcfzb", lambda c, k: c.finance_report(k, "zcfzb")),
    ("finance_report lyb", lambda c, k: c.finance_report(k, "lyb")),
    ("finance_report xjllb", lambda c, k: c.finance_report(k, "xjllb")),
    ("finance_diagnosis", lambda c, k: c.finance_diagnosis(k)),
    ("shareholders", lambda c, k: c.shareholders(k)),
    ("capital_structure", lambda c, k: c.capital_structure(k)),
    ("business_report", lambda c, k: c.business_report(k)),
    ("industry_analysis", lambda c, k: c.industry_analysis(k)),
    ("trading_report", lambda c, k: c.trading_report(k)),
    ("digest", lambda c, k: c.digest(k)),
    ("profit_forecast", lambda c, k: c.profit_forecast(k)),
    ("stock_score", lambda c, k: c.stock_score(k)),
    ("dividend_financing", lambda c, k: c.dividend_financing(k)),
    ("governance", lambda c, k: c.governance(k)),
    ("northbound_holding", lambda c, k: c.northbound_holding(k)),
    ("company_news", lambda c, k: c.company_news(k)),
    ("hot_topics", lambda c, k: c.hot_topics(k)),
    ("announcements", lambda c, k: c.announcements(k)),
    ("news", lambda c, k: c.news(k)),
    ("stock_stage_gain", lambda c, k: c.stock_stage_gain(k)),
    ("stock_main_funds", lambda c, k: c.stock_main_funds(k)),
    ("stock_industry_rank", lambda c, k: c.stock_industry_rank(k)),
    ("stock_industry_pct_rank", lambda c, k: c.stock_industry_pct_rank(k)),
    ("stock_pepb_percentile", lambda c, k: c.stock_pepb_percentile(k)),
    ("stock_history_trend", lambda c, k: c.stock_history_trend(k)),
    ("stock_valuation_percentile", lambda c, k: c.stock_valuation_percentile(k)),
    ("valuation", lambda c, k: c.valuation(k)),
    ("theme_market", lambda c, k: c.theme_market(k)),
]


def rows_of(r) -> int:
    return sum(len(rs.rows or ()) for rs in r.result_sets or ())


def main() -> None:
    c = F10Client(timeout=20.0)
    problems: list[str] = []
    total = empty = fail = 0
    for code, name, sector in LEADERS:
        line = []
        for mname, fn in ASHARE_METHODS:
            total += 1
            try:
                r = fn(c, code)
                n = rows_of(r)
                if n == 0:
                    empty += 1
                    line.append(f"{mname}=空")
            except Exception as exc:  # noqa: BLE001
                fail += 1
                line.append(f"{mname}=FAIL({type(exc).__name__})")
                problems.append(f"{code} {name} {mname}: {exc}")
        flag = "  <<< " + "; ".join(line) if line else "OK"
        print(f"{code} {name:8s} {sector:6s} {flag}", flush=True)
    print()
    print(f"总计 {total} 次调用：失败 {fail}，空 {empty}")
    if problems:
        print("失败明细（前 20）:")
        for p in problems[:20]:
            print("  ", p)


if __name__ == "__main__":
    t = threading.Thread(target=main, daemon=True)
    t.start()
    t.join(600)
    if t.is_alive():
        print("超时")
