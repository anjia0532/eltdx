"""查港股 hkf10 的 schq/pepb_band/fxysyfx 参数。"""
from __future__ import annotations

import re
import urllib.request
import gzip


def fetch(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"Referer": "http://www.treeid/", "Accept-Encoding": "gzip",
                      "User-Agent": "Mozilla/5.0"}
    )
    raw = urllib.request.urlopen(req, timeout=20).read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", "replace")


PAGES = [
    "skef10_hk_schq",
    "skef10_hk_sdfx",
    "skef10_hk_sdfx_pepb_band",
    "skef10_hk_sdfx_fxysyfx",
    "skef10_hk_sdfx_hqzft",
]

for page in PAGES:
    try:
        html = fetch(f"http://page2.tdx.com.cn:7615/site/sketchf10/hkf10/html/{page}.html")
    except Exception as exc:  # noqa: BLE001
        print(f"{page}: 抓取失败 {exc}")
        continue
    if "Error 404" in html[:300]:
        print(f"{page}: 404")
        continue
    print(f"===== {page} =====")
    for m in re.finditer(r'callName:\s*"([^"]+)"', html):
        # 该 callName 后 400 字符内的 queryParamFunc
        tail = html[m.end():m.end() + 500]
        q = re.search(
            r'queryParamFunc:\s*function\s*\([^)]*\)\s*\{\s*return\s*(\[[^\]]*\])', tail
        )
        params = q.group(1) if q else "(无)"
        print(f"  {m.group(1):34s} {params[:130]}")
    print()
