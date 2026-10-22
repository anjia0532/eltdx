"""排查期货 F10 剩余 0 行 Entry 的精确参数。

针对仓单日报 ckrb、库存报告 kcbg、指数历史价格 lsjg、现金分红 xjfh、
历史成份 lscfg、成份权重 cfgqz、新闻评论 xwpl 做参数穷举。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from eltdx.f10.client import F10Client  # noqa: E402

c = F10Client()


def q(entry: str, *params) -> str:
    try:
        r = c.params(entry, *params)
        n = sum(len(rs.rows or ()) for rs in r.result_sets or ())
        return str(n)
    except Exception as exc:  # noqa: BLE001
        return f"FAIL:{str(ex)[:30]}"


CODE = "rb"
print("=== 仓单日报 ckrb ===")
for p in [("1", CODE), (CODE, "1"), ("1", CODE, "20261020"), (CODE,), ("001", CODE)]:
    print(f"  {p}: {q('CWServ.qhf9_sp_ckrb_ckrb', *p)}")
print("=== 库存报告 kcbg ===")
for p in [("1", CODE), (CODE, "1"), ("1", CODE, "20261020"), (CODE,)]:
    print(f"  {p}: {q('CWServ.qhf9_sp_kcbg_kcbg', *p)}")
print("=== 指数历史价格 lsjg（399300）===")
for p in [("2", "399300"), ("1", "399300"), ("2", "399300", ""), ("3", "399300")]:
    print(f"  {p}: {q('CWServ.qhf9_gz_zszl_lsjg', *p)}")
print("=== 现金分红 xjfh ===")
for p in [("1", "000300", "", ""), ("1", "000300", "20251020", "20261020"), ("2", "000300", "", "")]:
    print(f"  {p}: {q('CWServ.qhf9_gz_zsgz_xjfh', *p)}")
print("=== 历史成份 lscfg ===")
for p in [("1", "399300"), ("1", "399300", ""), ("2", "399300"), ("1", "399300", "20261020")]:
    print(f"  {p}: {q('CWServ.qhf9_gz_cfg_lscfg', *p)}")
print("=== 成份权重 cfgqz ===")
for p in [("1", "399300"), ("1", "399300", ""), ("2", "399300"), ("001", "399300")]:
    print(f"  {p}: {q('CWServ.qhf9_gz_cfg_cfgqz', *p)}")
print("=== 新闻评论 xwpl ===")
for p in [("1", "399300"), ("1", "399300", ""), ("001", "399300"), ("399300",)]:
    print(f"  {p}: {q('CWServ.qhf9_gz_cfg_xwpl', *p)}")
