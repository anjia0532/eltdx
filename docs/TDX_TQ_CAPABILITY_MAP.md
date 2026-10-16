# 与通达信 TQ 的能力对照

这一页回答两个问题：

1. **eltdx 相对通达信 TQ（`tqcenter` / [TQ 量化文档](https://help.tdx.com.cn/quant/docs/markdown/mindoc-1ctuhthaq5qmg/)）覆盖了哪些能力**；
2. **哪些能力明确不做（定位差异）、哪些是真缺口（要别的通道）**——集中标注，方便按图索骥。

结论先行：eltdx 是**行情 + F10 资料的数据层**（免客户端、Rust 原生 7709 引擎 + 7615 HTTP
通道）；TQ 是**数据 + 公式 + 交易 + 回测的一体化平台**（必须启动并登录通达信终端）。
数据面上 eltdx 已覆盖 TQ 的绝大部分查询接口，公式引擎、交易通道和回测框架是定位差异，
不做对齐。

## 一、能力覆盖总览

| 能力域 | TQ 接口 | eltdx | 说明 |
| --- | --- | --- | --- |
| 行情快照 / 五档 / 分类 | `get_market_data` / `get_depth` / 分类行情 | ✅ `quotes.get_snapshots` / `quotes.get_depth` / `quotes.list_by_category` / `helpers.full_quotes` | eltdx 多一层五档自动合并 |
| K 线 / 分时 / 成交明细 | `get_market_data` / `get_transaction` | ✅ `bars.get` / `minutes.*` / `trades.*` | 含退市 K 线、复权系数、GBBQ |
| 板块 / 成份股 | `get_sector_list` / `get_stock_list_in_sector` | ✅ `helpers.board_quotes` / `board_member_quotes` / `topic_stocks` | 板块快照 + 涨停梯队 |
| 指数成份股 | `get_index_stocks` / `get_zzgz_stocklist` | ✅ `f10.index_members` / `helpers.index_members` | v3.4.4 新增 |
| 指数跟踪产品 | `get_trackzs_etf_info` | ✅ `f10.index_tracking_products` / `helpers.index_etfs` | v3.4.4 新增，方向相反：给指数找产品 |
| 外盘股票 | 美股行情接口 | ✅ `ex.MacExClient.goods_quotes` / `goods_kline`（`market=73/74/78`） | 美股 13409 只、德股 40 只、新加坡股 1392 只，实测见 [EXTENDED_MARKET.md](EXTENDED_MARKET.md) |
| 新股申购 | `get_ipo_info` | ✅ `f10.ipo_calendar` / `helpers.ipo_calendar` | v3.4.4 新增 |
| 财务数据 | `get_financial_data` | ✅ `corporate.finance_batch` / `f10.finance_report` | 字段级对齐，聚合口径见下方缺口 |
| 实时推送 | `subscribe_hq` / `subscribe` / `get_full_tick` | ✅ `quotes.subscribe` / `subscribe_hq` | v3.4.4 新增回调封装 |
| 自选股 / 自定义板块 | 读写 | ⚠️ 只读（写入不做） | 见「明确不做」 |
| 公式引擎 | `formula_set_data` / `formula_zb·xg·exp` / `formula_process_mul_*` | ❌ | 结构性缺失，见下 |
| 实盘 / 模拟交易 | `order_stock` / `query_stock_orders` 等 | ❌ | 结构性缺失，见下 |
| 回测框架 | Lambda `context` / `run_daily` / `get_profile_stats` | ❌ | 定位差异 |

### eltdx 反超项（TQ 没有，不必对齐）

- **免客户端**：TQ 必须启动通达信终端并登录；eltdx 全链路直连服务器。
- **F10 深度资料**：30+ 个分区（股东研究、行业分析、基金 / ETF、沪深股通、盈利预测、
  估值、题材对比、财务诊断、个股总评），TQ 只有文本包 `download_file`。
- **资金流向日数据**：`money_flow.daily` / `history` 的近 3/5/10/20/60 日主力 / 超大单 /
  大单净额序列。
- **板块分红成份**（v3.4.5）：`helpers.board_members(code)` 给出板块成份股的分红
  方案、进度、公告 / 登记 / 除权日和报告期，按记录身份去重翻页；TQ 的板块成份股
  接口不带分红维度。
- **短线打板生态**：竞价明细、连板天梯、题材强度、开盘量比、封单，TQ 需自己写公式。
- **本地复权系数 + GBBQ 审计、退市 K 线、vipdoc 离线解析**。

## 二、明确不做的能力（定位差异，不追）

| # | 能力 | TQ 接口 | 不做的理由 |
| --- | --- | --- | --- |
| 1 | 自定义板块写入（创建 / 删除 / 重命名 / 清空 / 添加成分股） | 客户端板块管理 | 写入要改用户本地客户端数据，超出免客户端数据层定位；eltdx 对 `blocknew` 只读 |
| 2 | 公式选股 | `formula_xg` / `formula_process_mul_xg` | 公式引擎整体缺失，依赖客户端公式的选股链路在 Python 侧重写指标 |
| 3 | 下单 / 撤单 / 查询 | `order_stock` / `cancel_order_stock` / `query_stock_*` | 交易需要券商通道与合规资质，数据层不做 |
| 4 | 回测与绩效归因 | Lambda `context` / `get_profile_stats` | eltdx 提供数据与指标，回测框架由调用方自行搭建或使用 TQ |

## 三、真缺口：eltdx 拿不到、需要别的通道的能力

| # | 能力 | TQ 接口 | 现状与替代通道 |
| --- | --- | --- | --- |
| 1 | **指数成份权重** | `get_index_weight` | 通达信系（7615 成份股 Entry、easy-tdx、腾讯源、新浪源）**都没有权重列**；中证系列指数用**中证官网权重文件**（见下方说明），客户端同样不提供 |
| 2 | **可转债专项数据** | `get_kzz_info` / `get_kzz_info_batch` | ⚠️ **通道已确认、待封装**（2026-10-16）：`CWServ.skef10_bond_kzz_*` 家族齐备——转股价、信用评级、赎回 / 回售 / 下修条款、利率、转股情况、发行人资料、公告全可取（见第五节）。仍缺：**溢价率**（无现成列，需自算 = 转债价 / 转股价值 − 1）、**十大持有人** `["sdcyr", code, 报告期]` 需显式报告期（两段式） |
| 3 | **ETF 申赎成分证券** | `download_file`（申赎清单） | ✅ **通道已确认、待封装**（2026-10-16）：`CWServ.skef10_jj_fxsy` 的 `["etfsscfzq", code, ""]`，实测 `510300` **300 只** / `588000` 50 只 / `159915` 100 只成分证券 + `ZXRQ` 最新日期（见第五节）。不再需要解析 PCF 文件 |
| 4 | **基金 F10 持股明细第二段** | — | ⚠️ 仍是两段式：`f10.fund_report(holdings / holdings_detail)` 只给报告期列表（第一段，`rq` 列），第二段请求的 Entry / Params 未确认。**同类问题的参数格式已确认**：可转债十大持有人用 `["sdcyr", code, "20260630"]`（`20260630` 或 `2026-06-30`）即得明细 10 行，说明服务端第二段普遍靠**报告期参数**驱动，基金持股明细可按此思路继续探 |
| 5 | **市场 / 板块级财务聚合** | `get_gpjy_value` / `get_bkjy_value` / `get_scjy_value` / `get_gp_one_data` | 这条**只指财务 / 经营指标**（净利润、ROE、经营性现金流一类）的市场 · 板块级**预聚合**口径：eltdx 有个股财务（`finance_batch` / `finance_report`）和板块成份股财务对比（`market_report(section="board_finance_compare")`，实测 `880472` 50 行 × 12 列），汇总要自己聚合近似。**不含资金流向 / 两融**——那两类 eltdx 已有市场 · 板块级预聚合，见下方说明 |

!!! note "资金流向 / 两融不是第 5 条的缺口（已预聚合，不必自己汇总）"

    这两类 eltdx 已直接给**市场 / 板块级汇总**：

    - **全市场两融日序列**：`market_report(section="market_margin_summary")`（`000001` 实测
      8676 行、2010-03-31 起，列含融资买入 / 融资余额 / 融券余额 / 两融余额 / 两融差额 /
      三大指数收盘价）；活跃个股 `market_margin`（1676 行）；投资者统计 `market_margin_investors`。
    - **板块资金**：`market_report(section="board_flow")`（`880472` 实测 51 行，`N005` 主力净额 +
      分档净额）；指数资金动向 `index_flow`。
    - **个股资金流向 60 日**：`money_flow.history(code, days=60)`——`N004` 主力净额、
      `N005` 超大单净买入、`N006` 大单净买入、`N007` 主买净额（实测 `600519` 60 行、
      日期降序、`days` 取 3/5/10/20/60）。
    - **估值百分位也不用自己算**：`f10.valuation(code, req_id="200191")` 的
      `PEBFW` / `PBBFW` / `PSBFW` / `PCFBFW` 就是服务端算好的分位。

    真正没预聚合的只有**财务 / 经营指标**的市场级口径（第 5 条），需要从
    `board_finance_compare` 的成份股行自行汇总。

!!! note "权重数据源实测结论（2026-10-15）"

    - **easy-tdx**：无指数权重接口（API 面里没有 weight / 成份权重方法）。
    - **腾讯源**：`ifzqgtimg` 行情接口无指数成份权重（`mktHs/rank?index=` 返回 TYPE_ERROR）。
    - **新浪源**：`Market_Center.getHQNodeData?node=hs300` 只有行情列，无权重；
      `vII_NewestComponent` 页面只有成份代码清单。
    - **中证官网（推荐，非东财）**：
      `https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/closeweight/{code}closeweight.xls`
      实测 `000300` 返回 301 行 × 10 列（含 `权重(%)`，报告期 20260930），
      覆盖中证 / 上证系列指数（综指等非中证管理指数不适用）；URL 变更频繁，
      生产使用建议包一层探测与告警。

## 四、哪些不用去客户端找

- **指数成份股清单、指数跟踪产品、新股列表**：v3.4.5 已由 eltdx 直接提供
  （`helpers.index_members` / `index_etfs` / `ipo_calendar`）。
- **外盘股票（美股 / 德股 / 新加坡股）**：扩展行情 MAC-EX 通道直接给数据
  （`market=74/73/78`，用法见 [EXTENDED_MARKET.md](EXTENDED_MARKET.md)）。
- **十大股东 / 经营分析 / 舆情题材 / 公司资讯**：7615 F10 结构化通道已有——
  `f10.shareholders(section="top")`（十大股东，列 `gd`/`rq`/`cgs`/`pos` 等）、
  `f10.business_report`（经营分析，主营概述 / 主营构成 / 前五客户供应商）、
  `f10.hot_topics`（题材，列 `ztmc`/`ztnr`/`ztrq` 等）、`f10.company_news` /
  `f10.digest`（新闻 / 公告 / 资讯），CLI 对应 `eltdx f10 shareholders|business|topics|news`。
- **板块分红成份**：`helpers.board_members`（见总览表反超项）。

## 五、已确认通道、待封装（2026-10-16 抓客户端 F10 缓存取证）

客户端点击 ETF 申赎成分证券（F10 → 投资组合）与可转债 F10（`110081`）后，
从 `T0002\tmp\Code Cache\js\*` 里的 `_key` URL 找到页面脚本，读出调用地址；
下面 Entry 与参数均**实测有数据**；其中指数估值快照（见 5.3）已在 v3.4.5 封装为
`market_report(section="index_valuation")`，其余仍待封装。

### 5.1 债券 / 可转债 F10：`CWServ.skef10_bond_*`（家族 `zqf10`）

客户端页面目录 `/site/sketchf10/zqf10/`，页面脚本 `skef10_zq_*.js`，按券种分子家族：

| 子家族 | 券种 | 页面 |
| --- | --- | --- |
| `skef10_zq_kzz_*` | **可转债** | `zqgk` / `cwfx` / `fxqk` / `zqdb` / `zqpj` / `zgqk` / `zqll` / `zqgg` |
| `skef10_zq_zq_*` | 转债（通用） | `zqtk` 转债条款 |
| `skef10_zq_gz_*` / `gzhg_*` | 国债 / 国债回购 | `zqgk` / `fxqk` / `zqsj` / `zqpj` |
| `skef10_zq_qyz_*` | 企业债 | `zqgk` / `cwfx` / `xjlfx` / `zqdb` / `zqpj` / `zqll` / `gsps` |
| `skef10_zq_zczq_*` | 资产支持证券 | `zqgk` / `cwfx` / `zqpj` |
| `skef10_zq_kjhz_*` | 可交换债 | `zqgk` / `cwfx` / `fxqk` / `zqdb` / `zqpj` / `jhqk` / `zqll` |

可转债（`110081` 闻泰转债）实测：

| Entry | Params | 结果 |
| --- | --- | --- |
| `CWServ.skef10_bond_kzz_zqgk` | `["zqzl", code, ""]` | 转债资料：**转股价 `jg` 18.36**、信用评级 `xypj` BBB-、评级机构 `pgjg`、起息 / 到期 / 转股期、余额、付息方式、发行方式 |
| `CWServ.skef10_bond_kzz_zqgk` | `["fhrjbzl", code, ""]` | 发行人及担保人资料（完整公司信息） |
| `CWServ.skef10_bond_kzz_zqgk` | `["xtfhr", code, ""]` | 相同发行人（`110081` 实测 0 行） |
| `CWServ.skef10_bond_kzz_zqgk` | `["sdcyr", code, 报告期]` | **十大持有人** 10 行（排名 / 名称 / 持仓量 / 占比）；报告期 `20260630` 或 `2026-06-30` 均可，不传则 `ErrorCode=-1005` |
| `CWServ.skef10_bond_kzz_fxqk` | `["fxqk", code]` | 发行情况 5 行 |
| `CWServ.skef10_bond_kzz_fxqk` | `["xjlfx", code]` | 现金流分析 5 行 |
| `CWServ.skef10_bond_kzz_zqdb` | `["dbsm", code]` | 对比说明（`110081` 实测 0 行） |
| `CWServ.skef10_bond_kzz_zg` | `["zgqk", code]` | **转股情况**（正股代码 / 名称、转股期起止） |
| `CWServ.skef10_bond_kzz_lltk` | `["hstk", code]` | **回售条款**（触发条件 30/30、阈值 70%、回售价、完整条款文字、当前 `t014` 触发计数） |
| `CWServ.skef10_bond_kzz_lltk` | `["shtk", code]` | **赎回条款**（15/30、130%、到期赎回价 108%） |
| `CWServ.skef10_bond_kzz_lltk` | `["xztk", code]` | **下修条款**（15/30、85%、修正底价说明） |
| `CWServ.skef10_bond_kzz_lltk` | `["zqll", code]` | **转债利率**（递进利率、逐年票息、到期赎回价） |
| `CWServ.skef10_bond_kzz_zqll` | `["zbz", code]` / `["zqll", code]` | 逐年票息表 / 利率表（各 6 行） |
| `CWServ.skef10_bond_kzz_zjzx` | `[code, sc]` | 转债公告 **40 条**（`rec_id` / `Title` / `Issue_date` / 巨潮 PDF `url`）；`sc` 传 `"1"`（沪）/ `"0"`（深），传 `"sh"` 无效 |

> **仍缺**：溢价率（`zqzl` 的 `N001`/`N002`/`N003` 是未标注列，语义未定）——可自算
> `溢价率 = 转债价格 / (100 / 转股价 × 正股价格) − 1`，正股价格走行情接口。

### 5.2 ETF 申赎成分证券：`CWServ.skef10_jj_fxsy`（`etfsscfzq`）

注意 callName 在 **`skef10_jj_fxsy`**（不在 `skef10_jj_tzzh`）——`tzzh` 页面点「ETF申赎成分证券」
tab 时切到 `fxsy` 的这个子命令：

| Entry | Params | 结果 |
| --- | --- | --- |
| `CWServ.skef10_jj_fxsy` | `["etfsscfzq", code, ""]` | 三张表：`table0` 是否 ETF（`N001`）、`table1` **成分证券**、`table2` 最新日期 `ZXRQ` |

成分证券列：`N001` 代码、`N002` 名称、`N003` 申购数量、`N004` 允许 / 禁止、
`N005`/`N007` 现金替代比例、`N006`/`N008` 替代金额。实测：

| 代码 | 成分证券行数 | `ZXRQ` |
| --- | --- | --- |
| `510300` 沪深300ETF | **300** | 20261016 |
| `588000` 科创50ETF | 50 | — |
| `159915` 创业板ETF | 100 | — |

### 5.3 指数 / 板块估值分析：`CWServ.skef10_zs_jbxx_gzxx`（深度分析页）

客户端指数 F10 → **深度分析（估值分析）**页，页面脚本 `zsf10/js/skef10_zs_ag_gzfx.js`：

| Entry | Params | 结果 |
| --- | --- | --- |
| `CWServ.skef10_zs_jbxx_gzxx` | `["001", code, "", ""]` | **估值快照** 1 行：`N001` 市盈率TTM、`N002` 市盈率LYR、`N003` 市净率MRQ、`N004` 市净率加权、`N005` 市销率TTM、`N006` 市销率LYR、`N007` 市现率TTM、`N008` 市现率LYR、`N009` 股息率(%)、`N010__2` 报告期 |
| `CWServ.skef10_bk_sdfx` | `["001", code, ""]` | 板块版估值表（**已封装** = `market_report(section="board_analysis")`），多 `N010` 净资产收益率、`N011` 更新日期 |

实测估值快照（`N010__2`=三季报）：

| 指数 | 市盈率TTM | 市净率MRQ | 市销率TTM | 市现率TTM | 股息率% |
| --- | --- | --- | --- | --- | --- |
| `000300` 沪深300 | 13.01 | 1.27 | 1.46 | 3.51 | 2.94 |
| `000001` 上证综指 | 15.10 | 1.29 | 1.40 | 3.92 | 2.61 |
| `399001` 深证成指 | 26.65 | 2.36 | 1.73 | 11.78 | 1.79 |

> **已封装的相关能力**：个股估值**历史序列**走 `f10.valuation(code, req_id="200191")`
> （`HQServ.hq_nlp_gpsj`），返回 `PETTM` / `PBMRQ` / `PSTTM` / `PCFOCFTTM` 及
> **百分位** `PEBFW` / `PBBFW` / `PSBFW` / `PCFBFW`（服务端已算好分位，不必自行聚合）、
> `PEG`、`AVGMVM` / `ALIQMV`，`table0.TotalNum` 给总条数（`600519` 1211 条分页取）。
> `req_id="200135"` 给年度估值统计（个股 / 指数均可，`000300` 22 行、`000001` 37 行）。
> **已封装（v3.4.5）**：上面这张指数估值快照 → `market_report(section="index_valuation")`。
> **仍未封装**：`ReqId=200134` 的指数收盘价序列（深度分析图的另一半数据源）。

### 5.4 顺带确认的规律（供继续探「第二段」用）

两段式请求的服务端形态是：第一段给列表（报告期 / 索引），第二段把列表里的值
填进参数再查。可转债十大持有人 `["sdcyr", code, "20260630"]` 即此模式；
基金 F10 持股明细（`fund_report(holdings / holdings_detail)`）的第二段可按同样
思路试 `cgqk` 系列的 `*bgq` / 报告期参数。
