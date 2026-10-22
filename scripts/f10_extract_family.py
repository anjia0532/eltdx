"""提取债券/行业/期货 F10 全家族的 Entry 与 Params。

从 page2.tdx.com.cn:7615 抓取 sketchf10 各家族 HTML，提取 callName(Entry)
与 queryParamFunc(Params)。用于封装 bond(债券全类型)/hy(行业)/qh(期货) F10。
"""
from __future__ import annotations

import json
import re
import urllib.request
import gzip
from pathlib import Path

BASE = "http://page2.tdx.com.cn:7615/site/sketchf10"
OUT = Path(__file__).resolve().parent.parent / "tmp_f10" / "f10_family_ext.json"

CALL_PAT = re.compile(
    r'callName:\s*"([^"]+)"(.*?)queryParamFunc:\s*function\s*\([^)]*\)\s*\{\s*return\s*(\[[^\]]*\])',
    re.S,
)
INLINE_PAT = re.compile(r'"(skef10_\w+)"\s*,\s*(\[[^\]]*\])')
ENTRY_PAT = re.compile(r'"(skef10_\w+)"')


def fetch(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"Referer": "http://www.treeid/", "Accept-Encoding": "gzip", "User-Agent": "Mozilla/5.0"},
    )
    raw = urllib.request.urlopen(req, timeout=20).read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", "replace")


def norm(text: str) -> list[str]:
    inner = text.strip().strip("[]")
    out: list[str] = []
    for p in re.split(r",\s*", inner):
        p = p.strip()
        if not p:
            continue
        p = re.sub(r"JsUrl\.(stock|code)", "{stock}", p)
        p = re.sub(r"JsUrl\.(\w+)", r"{\1}", p)
        p = re.sub(r"\bt\.(page|pageSize|value|sjfw|tabValue|hqzq)\b", r"{\1}", p)
        if p.startswith('"') and p.endswith('"'):
            p = p[1:-1]
        out.append(p)
    return out


def extract_menus(index_js: str) -> list[tuple[str, str]]:
    """从 index.js 提取 (label, page) 列表（page 为完整页面名）。

    兼容两种配置变量：``skef10_index_config``（对象）与 ``arrMenu``（数组）。
    """
    m = re.search(r"skef10_index_config=\{([\s\S]*?)\};", index_js)
    if m:
        return re.findall(r'\["([^"]+)","(skef10_\w+)"\]', m.group(1))
    m = re.search(r"arrMenu=\[([\s\S]*?)\];", index_js)
    if m:
        return re.findall(r'\["([^"]+)","(skef10_\w+)"\]', m.group(1))
    return []


def extract_family(family: str, index_js_url: str, entry_prefix: str) -> dict:
    idx = fetch(index_js_url)
    menus = extract_menus(idx)
    print(f"### {family}: {len(menus)} 个菜单")
    result: dict = {}
    for label, page in menus:
        url = f"{BASE}/{family}/html/{page}.html"
        try:
            html = fetch(url)
        except Exception as exc:
            print(f"  {label} {page}: 抓取失败 {exc}")
            continue
        if "Error 404" in html:
            print(f"  {label} {page}: 404")
            continue
        # 页面无内联 callName 时，回退抓它引用的外部 JS（如 hyzlan/qh 各页）。
        if "callName" not in html:
            for js_ref in re.findall(r'src="\.\./js/([\w.]+\.js)"', html):
                try:
                    html += "\n" + fetch(f"{BASE}/{family}/js/{js_ref}")
                except Exception:
                    pass
        seen: dict[str, set[tuple[str, ...]]] = {}
        for mm in CALL_PAT.finditer(html):
            seen.setdefault(mm.group(1), set()).add(tuple(norm(mm.group(3))))
        for name, pt in INLINE_PAT.findall(html):
            seen.setdefault(name, set()).add(tuple(norm(pt)))
        entries = []
        for name in sorted(set(ENTRY_PAT.findall(html))):
            if not name.startswith(entry_prefix):
                continue
            entries.append(
                {"entry": f"CWServ.{name}", "params": [list(p) for p in sorted(seen.get(name, set()))]}
            )
        result[page] = {"label": label, "entries": entries}
        print(f"  == {label} {page} ({len(entries)})")
        for e in entries:
            print(f"     {e['entry']:38s} {e['params']}")
    return result


def main() -> None:
    out: dict = {}
    out["bond"] = extract_family("zqf10", f"{BASE}/zqf10/js/skef10_zq_index.js", "skef10_bond_")
    out["industry"] = extract_family("hyf10", f"{BASE}/hyf10/js/skef10_hy_index.js", "skef10_hy_")
    out["futures"] = extract_family("qhf10", f"{BASE}/qhf10/js/skef10_qh_index.js", "skef10_qh_")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    total = sum(len(v["entries"]) for fam in out.values() for v in fam.values())
    print(f"\n总计 {total} 个 Entry，已写入 {OUT}")


if __name__ == "__main__":
    main()
