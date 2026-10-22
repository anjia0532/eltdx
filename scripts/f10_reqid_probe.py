"""分析 gg_ggzp.js / gg_sdfx.js / gg_zxts.js 的 ReqId 用途与参数。"""
from __future__ import annotations

import re
from pathlib import Path

JS_DIR = Path("C:/Users/AnJia/AppData/Local/Temp/f10_js/tdxf10")


def show(page: str, reqids: list[str]) -> None:
    data = (JS_DIR / f"{page}.js").read_text(encoding="utf-8", errors="replace")
    print(f"########## {page}.js ##########")
    for rid in reqids:
        for m in re.finditer(rf'ReqId:\s*"{rid}"', data):
            s = max(0, m.start() - 260)
            e = min(len(data), m.start() + 320)
            print(f"--- ReqId={rid} ---")
            print(data[s:e].replace("\n", " ")[:560])
            print()
            break  # 每个 ReqId 只看第一处
    print()


def show_entry(page: str, entry: str) -> None:
    data = (JS_DIR / f"{page}.js").read_text(encoding="utf-8", errors="replace")
    print(f"########## {page}.js 的 {entry} ##########")
    for m in re.finditer(re.escape(entry), data):
        s = max(0, m.start() - 200)
        e = min(len(data), m.start() + 300)
        print(data[s:e].replace("\n", " ")[:480])
        print("---")
    print()


if __name__ == "__main__":
    show("gg_ggzp", ["200740", "200741", "200742", "200744", "200745", "200747", "200192", "200743"])
    show("gg_sdfx", ["200124", "200135", "200192", "200191"])
    show_entry("gg_zxts", "zxtscwbq")
