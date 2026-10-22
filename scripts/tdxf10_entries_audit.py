"""提取 tdxf10 各页面 JS 的 Entry/ReqId，与本地封装比对找遗漏。"""
from __future__ import annotations

import json
import re
from pathlib import Path

JS_DIR = Path(__file__).resolve().parent / "tdxf10"
if not JS_DIR.is_dir():
    JS_DIR = Path("C:/Users/AnJia/AppData/Local/Temp/f10_js/tdxf10")

# 本地已封装的 Entry / ReqId（来自 f10/client.py 的方法）
LOCAL_ENTRIES = {
    "tdxf10_gg_comreq", "tdxf10_gg_gsgk", "tdxf10_gg_jyfx", "tdxf10_gg_gdyj",
    "tdxf10_gg_gdyj_jgcgmx", "tdxf10_gg_gbjg", "tdxf10_gg_gbjg_xsjjmx",
    "tdxf10_gg_fhrz", "tdxf10_gg_fhrz_zfhpmx", "tdxf10_gg_cwfx", "tdxf10_gg_cwfx_cbdp",
    "tdxf10_gg_cwzd", "tdxf10_gg_ggzp", "tdxf10_gg_rdtc", "tdxf10_gg_rdtc_gndb",
    "tdxf10_gg_ybpj", "tdxf10_gg_zxts", "tdxf10_gg_zxts_rqpm", "tdxf10_gg_zxtstzzhd",
    "tdxf10_gg_gszx", "tdxf10_gg_hyfx", "tdxf10_gg_jyds", "tdxf10_gg_sj",
    "tdxf10_gg_kbgs", "tdxf10_gg_zbyz", "tdxf10_gg_zlcc", "tdxf10_gg_idreq",
}
LOCAL_REQIDS = {"200191", "200743"}  # valuation / theme_market


def main() -> None:
    found_entries: dict[str, set[str]] = {}
    found_reqids: dict[str, set[str]] = {}
    for js_file in sorted(JS_DIR.glob("*.js")):
        data = js_file.read_text(encoding="utf-8", errors="replace")
        page = js_file.stem
        # callName:"xxx" 或 CallTQL(cb,"xxx")
        for m in re.finditer(r'callName:\s*"([\w.]+)"', data):
            name = m.group(1)
            if "CWServ." in name or "HQServ." in name:
                found_entries.setdefault(name, set()).add(page)
            else:
                found_entries.setdefault(f"CWServ.{name}", set()).add(page)
        for m in re.finditer(r'ReqId:\s*"(\d+)"', data):
            found_reqids.setdefault(m.group(1), set()).add(page)

    print("=== 页面 JS 出现的全部 Entry ===")
    for e in sorted(found_entries):
        bare = e.replace("CWServ.", "").replace("HQServ.", "")
        mark = ""
        if e.startswith("CWServ.tdxf10") and bare not in LOCAL_ENTRIES:
            mark = "  <<< 未封装"
        if e.startswith("HQServ.") or e.startswith("CWSearch.") or e.startswith("JJSServ."):
            mark = "  (服务)"
        print(f"  {e:36s} 页面={sorted(found_entries[e])}{mark}")

    print()
    print("=== 页面 JS 出现的 ReqId ===")
    for r in sorted(found_reqids):
        mark = "  <<< 未封装" if r not in LOCAL_REQIDS else ""
        print(f"  ReqId={r} 页面={sorted(found_reqids[r])}{mark}")

    # 与本地源码再核对一次（防上面清单过期）
    src = Path("D:/AnJia/Work/workspace/python/eltdx/src/eltdx/f10/client.py")
    src_text = src.read_text(encoding="utf-8")
    print()
    print("=== 源码实测核对 ===")
    for e in sorted(found_entries):
        if e.startswith("CWServ.tdxf10"):
            in_src = e in src_text
            print(f"  {e:36s} 源码{'有' if in_src else '无'}  {'' if in_src else '<<< 遗漏'}")
    for r in sorted(found_reqids):
        in_src = f'"{r}"' in src_text
        print(f"  ReqId={r:8s} 源码{'有' if in_src else '无'}  {'' if in_src else '<<< 遗漏'}")


if __name__ == "__main__":
    main()
