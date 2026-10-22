# 通达信美股(mgf10) / 港股(hkf10) F10 全家族逆向清单

> 逆向自通达信客户端 `new_tdx64` 的 JS 缓存 + `page2.tdx.com.cn:7615` 网关。
> 所有 Entry 均经 `POST TQLEX?Entry=...` 实测可用（见文末验证）。

## 一、调用机制

- **Entry 命名**：`CWServ.skef10_mg_*`（美股）、`CWServ.skef10_hk_*`（港股）。
  JS 里 `callName:"skef10_mg_xxx"` → 网关 Entry = `CWServ.` + callName（无 `.` 时）。
- **请求**：`POST http://<网关>:7615/TQLEX?Entry=CWServ.skef10_mg_xxx`
  body = `{"Params":[...]}`（JSON）。
- **代码格式**：美股 = 裸代码（`NVDA`）；港股 = 5 位数字（`00700`）。
- **网关**：`page2.tdx.com.cn:7615`（有 `HitCache`/`hitCache` 二级缓存）；`static.tdx.com.cn:7615`（无缓存）。eltdx 现用 `static.tdx.com.cn`。
- **Params 约定**：`{stock}` = 代码；`{page}`/`{pageSize}` = 分页；`{value}`/`{sjfw}`/`{tabValue}`/`{hqzq}` = 交互变量。

## 二、美股 mgf10 全家族（16 菜单 / 17 Entry）

| 菜单 | Entry | Params |
|---|---|---|
| 最新提示 | `skef10_mg_idreq` | `["name", {stock}]` |
| | `skef10_mg_zxdt` | `["zxdt"\|"sypl"\|"gsgy"\|"zysj", {stock}, ""]` |
| 公司概况 | `skef10_mg_gsgk` | `["001", {stock}]` |
| 财务分析 | `skef10_mg_cwfx` | `["zcfzb"\|"lyb"\|"xjllb", {stock}]` |
| 财务指标 | `skef10_mg_cwzb` | `["jbzb"\|"cznl"\|"yynl"\|"ylnl"\|"ccznl", {stock}]`、`["006", {stock}]` |
| 经营分析 | `skef10_mg_jyfx` | `[{stock}]` |
| 行业分析 | `skef10_mg_hyfx` | `["001", {stock}, "4", "1"]` |
| 行业对比 | `skef10_mg_hydb` | `["001", {stock}, "", "0", "0"]` |
| 分红融资 | `skef10_mg_fhrz` | `[{stock}, "fh"\|"cf"]` |
| 股本结构 | `skef10_mg_gbjg` | `["001", {stock}, 1]`、`["002", {stock}, {page}]` |
| 股东权益 | `skef10_mg_gbgd` | `["006", {stock}, 1, 10]`、`["003"\|"004"\|"005"\|"007"\|"008"\|"011"\|"014", {stock}, {page}, {pageSize}]` |
| 董事高管 | `skef10_mg_dsgg` | `[{stock}, "t"]` |
| 市场行情 | `skef10_mg_schq` | `["001", {stock}, {page}, {pageSize}]`、`["003", {stock}, 0, i]` |
| 公司资讯 | `skef10_mg_idreq` | `["name", {stock}]` |
| | `skef10_mg_gsbd` | `["gsgg", {stock}]`（gsgg=公司公告） |
| 公司评级 | `skef10_mg_gspj` | `["001"\|"002"\|"003", {stock}]` |
| 热点题材 | `skef10_mg_rdtc` | `["001", {stock}, "", 4, 1]` |
| 深度分析 | `skef10_mg_sdfx` | `["001", {stock}]`、`["002", {stock}]` |

## 三、港股 hkf10 全家族（15 菜单 / 24 Entry）

| 菜单 | Entry | Params |
|---|---|---|
| 最新提示 | `skef10_hk_idreq` | `["name", {stock}]` |
| | `skef10_hk_zxts` | `["1".."5", {stock}]` |
| | `skef10_hk_zxts_kbgs` | `["0"\|"1"\|"t", {stock}]` |
| 公司大事 | `skef10_hk_gsds` | `["1".."6", {stock}]` |
| 公司概况 | `skef10_hk_gsgk` | `["1".."6", {stock}]` |
| 关联证券 | `skef10_hk_glzq` | `["6", {stock}]`、`[{value}, {stock}]` |
| 高管资料 | `skef10_hk_ggzl` | `["1"\|"2"\|"3", {stock}]` |
| 股本结构 | `skef10_hk_gbjg` | `["1"\|"2"\|"3", {stock}]` |
| 股东持股 | `skef10_hk_gdcg` | `["1".."13", {stock}, ""]` |
| 财务分析 | `skef10_hk_cwfx` | `["zcfzb"\|"zhsyb"\|"xjllb", {stock}]` |
| 财务指标 | `skef10_hk_cwzb` | `["jbzb"\|"cznl"\|"yynl"\|"ylnl"\|"ccznl", {stock}]`、`["6", {stock}]` |
| 经营分析 | `skef10_hk_jyfx` | `[子标签, {stock}]` |
| 行业比较 | `skef10_hk_hybj` | `["1"\|"3", {stock}, "0", "0"]` |
| 市场行情 | `skef10_hk_schq` | `["1".."7", {stock}]` |
| | `skef10_hk_schq_zjlx` | `["001"\|"003", {stock}, ...]` |
| 公司资讯 | `skef10_hk_gszx` | `["3"\|"4", {stock}]` |
| 热点题材 | `skef10_hk_rdtc` | `["001", {stock}, "", "0", "0"]` |
| 深度分析 | `skef10_hk_sdfx_fxysyfx` | `[{stock}, {日期1}, {日期2}]`（分析师盈利预测，两日期去 `-`） |
| | `skef10_hk_sdfx_gzfx` | `[{stock}, {id}]`（估值分析） |
| | `skef10_hk_sdfx_hqzft` | `[{stock}]`（行情涨跌图） |
| | `skef10_hk_sdfx_pepb_band` | `["001", {stock}, {sjfw}, {tabValue}, {hqzq}]`（PE/PB band） |

## 四、实测验证（page2 网关，均 hitCache:true）

| Entry | Params | 返回 |
|---|---|---|
| `skef10_mg_idreq` | `["name","NVDA"]` | 英伟达 / NVDA ✅ |
| `skef10_mg_gsgk` | `["001","NVDA"]` | NVDA、英伟达、纳斯达克、1999-01-22 ✅ |
| `skef10_mg_cwfx` | `["zcfzb","NVDA"]` | 80 条资产负债表 ✅ |
| `skef10_hk_idreq` | `["name","00700"]` | 腾讯控股、sc=31 ✅ |
| `skef10_hk_gsgk` | `["1","00700"]` | 腾讯控股有限公司（含公司简介等 22 列）✅ |

## 五、与 eltdx 集成要点

1. **新增 `skef10_mg_*` / `skef10_hk_*` Entry 封装**：现有 `F10Client` 的 `params(entry, *params)` 已可直接调用，无需改底层。
2. **代码解析**：现有 `normalize_code` 只认 A 股 6 位数字，需扩展支持美股字母代码（`NVDA`）与港股 5 位代码（`00700`，前导 0 需保留）。
3. **网关选择**：若要命中 `HitCache`（服务端二级缓存），需用 `page2.tdx.com.cn:7615`；当前 `DEFAULT_TQLEX_BASE_URL` 是 `static.tdx.com.cn:7615`。
4. **Params 首参是「子标签」**：财务分析/指标等 Entry 的 Params[0] 是子标签（zcfzb/lyb/cwzb/…），封装时应作为 section 语义暴露，而非裸传。

## 六、待补项

- `skef10_mg_gsbd`（美股公司资讯子 Entry）精确参数
- `skef10_hk_sdfx_hqzft` / `skef10_hk_sdfx_fxysyfx` / `skef10_hk_sdfx_gzfx` 精确参数
- 各 Entry 返回列的字段中文映射（可复用 A 股 fields.py 思路另建 mg/hk 字段表）

原始抓取数据与完整 JSON：`tmp_f10/f10_family.json`；提取脚本：`scripts/f10_extract.py`。
