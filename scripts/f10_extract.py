"""从通达信 sketchf10 的 HTML 提取美股/港股 F10 的 Entry 全集与 Params（完整版）。

提取三种调用形式：
  A. callName:"X", ... queryParamFunc:function(t){return[...]}   (tdxGrid 配置)
  B. CallTQL(cb, "X", [...], {})  内联
  C. 内嵌 Entry 字符串

输出: tmp_f10/f10_family.json
"""
from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

BASE = "http://page2.tdx.com.cn:7615"

FAMILY = {
    "mgf10": [
        ("最新提示", "skef10_mg_zxts"), ("公司概况", "skef10_mg_gsgk"),
        ("财务分析", "skef10_mg_cwfx"), ("财务指标", "skef10_mg_cwzb"),
        ("经营分析", "skef10_mg_jyfx"), ("行业分析", "skef10_mg_hyfx"),
        ("行业对比", "skef10_mg_hydb"), ("分红融资", "skef10_mg_fhrz"),
        ("股本结构", "skef10_mg_gbjg"), ("股东权益", "skef10_mg_sdgd"),
        ("董事高管", "skef10_mg_dsgg"), ("市场行情", "skef10_mg_schq"),
        ("公司资讯", "skef10_mg_gszx"), ("公司评级", "skef10_mg_gspj"),
        ("热点题材", "skef10_mg_rdtc"), ("深度分析", "skef10_mg_sdfx"),
    ],
    "hkf10": [
        ("最新提示", "skef10_hk_zxts"), ("公司大事", "skef10_hk_gsds"),
        ("公司概况", "skef10_hk_gsgk"), ("关联证券", "skef10_hk_glzq"),
        ("高管资料", "skef10_hk_ggzl"), ("股本结构", "skef10_hk_gbjg"),
        ("股东持股", "skef10_hk_gdcg"), ("财务分析", "skef10_hk_cwfx"),
        ("财务指标", "skef10_hk_cwzb"), ("经营分析", "skef10_hk_jyfx"),
        ("行业比较", "skef10_hk_hybj"), ("市场行情", "skef10_hk_schq"),
        ("公司资讯", "skef10_hk_gszx"), ("热点题材", "skef10_hk_rdtc"),
        ("深度分析", "skef10_hk_sdfx"),
    ],
}

HEADERS = {
    "Referer": "http://www.treeid/",
    "Accept-Encoding": "gzip",
    "User-Agent": "Mozilla/5.0",
}

# 形式 A：callName + queryParamFunc（中间可能含嵌套对象，用非贪婪）
CALL_PAT = re.compile(
    r'callName:\s*"([^"]+)"(.*?)queryParamFunc:\s*function\s*\([^)]*\)\s*\{\s*return\s*(\[[^\]]*\])',
    re.S,
)
# 形式 B：CallTQL(cb, "Entry", [...], ...)
CALLTQL_PAT = re.compile(
    r'CallTQL\(\s*function\s*\([^)]*\)\s*\{[^{}]*\}\s*,\s*"(skef10_(?:mg|hk)_\w+)"\s*,\s*(\[[^\]]*\])',
    re.S,
)
ENTRY_STR_PAT = re.compile(r'"(skef10_(?:mg|hk)_\w+)"')


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read()
    if raw[:2] == b"\x1f\x8b":
        import gzip
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", errors="replace")


def norm_params(text: str) -> list[str]:
    inner = text.strip().strip("[]")
    if not inner.strip():
        return []
    out = []
    for p in re.split(r",\s*", inner):
        p = p.strip()
        if not p:
            continue
        # 变量占位符
        p = re.sub(r"JsUrl\.(stock|code)", "{stock}", p)
        p = re.sub(r"JsUrl\.(\w+)", r"{\1}", p)
        p = re.sub(r"\bt\.(page|pageSize|sjfw|tabValue|hqzq|pageNo|page_size)\b", r"{\1}", p)
        # 去掉引号
        if p.startswith('"') and p.endswith('"'):
            p = p[1:-1]
        out.append(p)
    return out


def extract(html: str) -> list[dict]:
    seen: dict[str, set] = {}
    for m in CALL_PAT.finditer(html):
        name, _, params_text = m.group(1), m.group(2), m.group(3)
        seen.setdefault(name, set()).add(tuple(norm_params(params_text)))
    for m in CALLTQL_PAT.finditer(html):
        name, params_text = m.group(1), m.group(2)
        seen.setdefault(name, set()).add(tuple(norm_params(params_text)))

    all_names = sorted(set(ENTRY_STR_PAT.findall(html)))
    result = []
    for name in all_names:
        params_list = [list(p) for p in seen.get(name, set())]
        result.append({
            "entry": f"CWServ.{name}" if "." not in name else name,
            "call_name": name,
            "params": params_list,
            "inline": bool(params_list),
        })
    return result


def main() -> None:
    out_dir = Path(__file__).resolve().parent.parent / "tmp_f10"
    out_dir.mkdir(exist_ok=True)
    summary: dict[str, list] = {}
    for dirname, menus in FAMILY.items():
        for menu_name, html_name in menus:
            url = f"{BASE}/site/sketchf10/{dirname}/html/{html_name}.html"
            try:
                html = fetch(url)
            except Exception as e:  # noqa: BLE001
                summary.setdefault(dirname, []).append(
                    {"menu": menu_name, "html": html_name, "error": str(e), "entries": []}
                )
                continue
            entries = extract(html)
            summary.setdefault(dirname, []).append(
                {"menu": menu_name, "html": html_name, "entries": entries}
            )

    (out_dir / "f10_family.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # 汇总去重
    all_entries: dict[str, dict] = {}
    for dirname, items in summary.items():
        for item in items:
            for e in item.get("entries", []):
                name = e["call_name"]
                rec = all_entries.setdefault(name, {"entry": e["entry"], "params": [], "menus": []})
                rec["menus"].append(f"{dirname}:{item['menu']}")
                for p in e["params"]:
                    if p not in rec["params"]:
                        rec["params"].append(p)

    print("========== 去重后的 Entry 全集 ==========")
    for name in sorted(all_entries):
        rec = all_entries[name]
        menus = " | ".join(sorted(set(rec["menus"])))
        if rec["params"]:
            print(f"{rec['entry']:42s} {rec['params']}  [{menus}]")
        else:
            print(f"{rec['entry']:42s} (Params未提取)  [{menus}]")
    n_ok = sum(1 for r in all_entries.values() if r["params"])
    print(f"\n共 {len(all_entries)} 个唯一 Entry，其中 {n_ok} 个提取到 Params")
    print(f"已写入 {out_dir / 'f10_family.json'}")


if __name__ == "__main__":
    main()
