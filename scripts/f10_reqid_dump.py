"""深挖未封装 ReqId 的完整 ResultSet 结构。"""
from __future__ import annotations

import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path("D:/AnJia/Work/workspace/python/eltdx/src").resolve()))

from eltdx.f10.client import F10Client  # noqa: E402


def dump(client: F10Client, label: str, entry: str, body: list, limit: int = 2) -> None:
    try:
        r = client.call(entry, body)
        print(f"--- {label} ---")
        for ti, rs in enumerate(r.result_sets or ()):
            cols = list(rs.columns or ())
            rows = rs.rows or ()
            if not cols:
                continue
            print(f"  [t{ti}] {len(rows)}行 cols={cols[:14]}")
            for row in rows[:limit]:
                print(f"      { {k: row[k] for k in cols[:8]} }")
    except Exception as exc:  # noqa: BLE001
        print(f"--- {label} --- FAIL {type(exc).__name__}: {str(exc)[:60]}")


def main() -> None:
    c = F10Client(timeout=15.0)
    CODE, SC = "601318", 1
    dump(c, "200740 阶段涨幅", "HQServ.hq_nlp_tcihq",
         [{"ReqId": "200740", "setcode": SC, "code": CODE, "zq_num": "60",
           "Page": -1, "PageSize": "10", "modname": "mod_tcihq.dll"}])
    dump(c, "200742 主力资金", "HQServ.hq_nlp_tcihq",
         [{"ReqId": "200742", "setcode": SC, "code": CODE, "zq_num": "30",
           "Page": -1, "PageSize": "10", "modname": "mod_tcihq.dll"}])
    dump(c, "200744 关联板块个股", "HQServ.hq_nlp_tcihq",
         [{"ReqId": "200744", "setcode": 1, "code": "881001",
           "Page": -1, "PageSize": -1, "modname": "mod_tcihq.dll"}])
    dump(c, "200745 行业归属排名", "HQServ.hq_nlp_tcihq",
         [{"ReqId": "200745", "setcode": SC, "code": CODE, "zq_num": "30",
           "Page": -1, "PageSize": "10", "modname": "mod_tcihq.dll"}])
    dump(c, "200747 支撑压力", "HQServ.hq_nlp_tcihq",
         [{"ReqId": "200747", "setcode": SC, "code": CODE, "zq_num": "30",
           "Page": -1, "PageSize": "10", "modname": "mod_tcihq.dll"}])
    dump(c, "200124 PE/PB分位", "HQServ.hq_nlp_gpsj",
         [{"ReqId": "200124", "code": CODE, "setcode": SC, "sjfw": "1y",
           "sdate": "", "edate": "", "zb": "pe_ttm", "hqzq": "1", "cwppgz": 1,
           "jglx": 0, "Page": 1, "PageSize": "300", "modname": "mod_gpsj.dll"}])
    dump(c, "200135 历史走势", "HQServ.hq_nlp_gpsj",
         [{"ReqId": "200135", "code": CODE, "setcode": SC, "modname": "mod_gpsj.dll"}])
    dump(c, "200192 估值分位", "HQServ.hq_nlp_gpsj",
         [{"ReqId": "200192", "Code": f"{CODE}|{SC}", "BeginDate": "0",
           "EndDate": "0", "Type": "0", "Page": "-1", "PageSize": "5",
           "modname": "mod_gpsj.dll"}])


if __name__ == "__main__":
    t = threading.Thread(target=main, daemon=True)
    t.start()
    t.join(150)
    if t.is_alive():
        print("超时")
