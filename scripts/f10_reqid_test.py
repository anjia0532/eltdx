"""实测未封装的 ReqId/Entry（用中国平安 601318 与茅台 600519）。"""
from __future__ import annotations

import json
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path("D:/AnJia/Work/workspace/python/eltdx/src").resolve()))

from eltdx.f10.client import F10Client  # noqa: E402


def probe(client: F10Client, label: str, entry: str, body: list) -> None:
    try:
        r = client.call(entry, body)
        rows: list = []
        for rs in r.result_sets or ():
            rows.extend(rs.rows or ())
        if rows:
            keys = list(rows[0].keys())[:12]
            print(f"  {label:28s} OK rows={len(rows)} cols={keys}")
            print(f"      首行={ {k: rows[0][k] for k in keys[:6]} }")
        else:
            print(f"  {label:28s} 空")
    except Exception as exc:  # noqa: BLE001
        print(f"  {label:28s} FAIL {type(exc).__name__}: {str(exc)[:60]}")


def main() -> None:
    c = F10Client(timeout=15.0)
    for code, sc in [("601318", 1), ("600519", 1)]:
        print(f"===== {code} (sc={sc}) =====")
        # hq_nlp_tcihq 家族（个股总评 ggzp）
        probe(c, "tcihq 200740 阶段涨幅", "HQServ.hq_nlp_tcihq",
              [{"ReqId": "200740", "setcode": sc, "code": code, "zq_num": "60",
                "Page": -1, "PageSize": "10", "modname": "mod_tcihq.dll"}])
        probe(c, "tcihq 200742 主力资金", "HQServ.hq_nlp_tcihq",
              [{"ReqId": "200742", "setcode": sc, "code": code, "zq_num": "30",
                "Page": -1, "PageSize": "10", "modname": "mod_tcihq.dll"}])
        probe(c, "tcihq 200744 关联板块个股", "HQServ.hq_nlp_tcihq",
              [{"ReqId": "200744", "setcode": 1, "code": "881001",
                "Page": -1, "PageSize": -1, "modname": "mod_tcihq.dll"}])
        probe(c, "tcihq 200745 ?", "HQServ.hq_nlp_tcihq",
              [{"ReqId": "200745", "setcode": sc, "code": code, "zq_num": "30",
                "Page": -1, "PageSize": "10", "modname": "mod_tcihq.dll"}])
        probe(c, "tcihq 200747 支撑压力", "HQServ.hq_nlp_tcihq",
              [{"ReqId": "200747", "setcode": sc, "code": code, "zq_num": "30",
                "Page": -1, "PageSize": "10", "modname": "mod_tcihq.dll"}])
        # hq_nlp_gpsj 家族（深度分析 sdfx）
        probe(c, "gpsj 200124 PE分位", "HQServ.hq_nlp_gpsj",
              [{"ReqId": "200124", "code": code, "setcode": sc, "sjfw": "1y",
                "sdate": "", "edate": "", "zb": "pe_ttm", "hqzq": "1", "cwppgz": 1,
                "jglx": 0, "Page": 1, "PageSize": "300", "modname": "mod_gpsj.dll"}])
        probe(c, "gpsj 200135 历史走势", "HQServ.hq_nlp_gpsj",
              [{"ReqId": "200135", "code": code, "setcode": sc, "modname": "mod_gpsj.dll"}])
        probe(c, "gpsj 200192 估值分位", "HQServ.hq_nlp_gpsj",
              [{"ReqId": "200192", "Code": f"{code}|{sc}", "BeginDate": "0",
                "EndDate": "0", "Type": "0", "Page": "-1", "PageSize": "5",
                "modname": "mod_gpsj.dll"}])
        # zxtscwbq 财务指标权重
        probe(c, "zxtscwbq 财务权重", "CWServ.tdxf10_gg_zxtscwbq", [code, "zcfzb"])
        print()


if __name__ == "__main__":
    t = threading.Thread(target=main, daemon=True)
    t.start()
    t.join(120)
    if t.is_alive():
        print("超时")
