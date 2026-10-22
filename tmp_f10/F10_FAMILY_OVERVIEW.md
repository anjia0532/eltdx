# eltdx F10 全家族封装总览

> 数据源：通达信 TQLEX 网关。A 股走 `static.tdx.com.cn:7615`；
> 扩展家族（美股/港股/新三板/债券/行业/期货）走 `page2.tdx.com.cn:7615`
> （带服务端二级缓存 `HitCache`）。
> 逆向脚本：`scripts/f10_extract.py`（mg/hk）、`scripts/f10_extract_family.py`（债券/行业/期货）。

## 一、家族总表

| 家族 | Entry 前缀 | 网关 | 代码格式 | 封装方法数 |
|---|---|---|---|---|
| A 股个股 | `CWServ.tdxf10_gg_*` | static | 6 位数字 | `company_profile`/`finance_report` 等 |
| A 股基金 | `CWServ.skef10_jj_*` | page2 | 6 位数字 | `fund_report`（30+ section） |
| 板块/指数/大盘 | `CWServ.skef10_bk_/zs_/dpzx_*` | page2 | 板块/指数代码 | `market_report`（30+ section） |
| 美股 | `CWServ.skef10_mg_*` | page2 | 裸字母码 `NVDA` | 17 |
| 港股 | `CWServ.skef10_hk_*` | page2 | 5 位 `00700` | 19 |
| 新三板 | `CWServ.skef10_sb_*` | page2 | 6 位数字 | 13 |
| 债券·可转债 | `CWServ.skef10_bond_kzz_*` | page2 | 6 位数字 | 6 |
| 债券·其余 8 类 | `CWServ.skef10_bond_{gz,qyz,gzhg,kjhz,zczq}_*` | page2 | 6 位数字 | 24 |
| 行业 | `CWServ.skef10_hy_*` | page2 | 板块代码 `881319` | 14 |
| 期货 | `CWServ.qhf9_{sp,gz}_*` | page2 | 品种 `rb`/股指 `IF` | 9 |

## 二、债券家族（本次补齐，9 类全覆盖）

债券 F10 共 9 类：国债回购 `gzhg`、国债 `gz`、地方政府债 `gzdfz`（复用 gz）、
中央政府债 `gzzcz`（复用 gz）、可转债 `kzz`、企业债 `qyz`、公司债 `gsz`（复用 qyz）、
可交换债 `kjhz`、ABS `zczq`。

### 参数模式（实测确认，不实测必错）

| 模式 | Entry | 说明 |
|---|---|---|
| `[section, code, sc]` | gz_*/qyz_*/kjhz_*/zczq_* | `sc` 市场码：`1`=沪、`0`=深 |
| `[section, code]` | kzz_*（sc 可空）、gzhg_*（无 sc） | 可转债忽略 sc；回购无 sc |
| `[code, sc]` | `skef10_bond_zjzx` 公告 | 无 section |

`sc` 与 `MacClient` 的 market 约定一致。沪深债券代码段高度重叠
（110/113/120/122/124 等两市都有），`_bond_sc()` **不纯代码段推断**，
默认沪市（`1`）；深市须显式 `sz` 前缀。

### 方法清单

```python
c = F10Client()
# 国债（019547 = 16国债19）
c.gz_profile("019547")              # 债券概况 zqgk / 发行概况 fxgk
c.gz_interest("019547")             # 付息情况 fxqk / 付息兑付 xjlfx
c.gz_market_data("019547")          # 大宗交易 dzjy / 招标比例 zsbl
c.gz_rating("019547")               # 地方债评级 dfzf
c.gz_finance("019547")              # 财务分析
# 企业债/公司债（122000）
c.qyz_profile("122000")             # 债券资料 zqzl / 信托发行人 xtfhr / 发行人信息 fhrjbzl
c.qyz_interest("122000")            # 付息兑付 fxqk / xjlfx / 份额变动 febd
c.qyz_guarantee("122000")           # 担保说明 dbsm
c.qyz_rating("122000")              # 中债评级 zjpjzst / 信用评级 zjxypj / 机构评级 fxjgpj
c.qyz_rate("122000")                # 债券利率 zqlv
c.qyz_review("122000")              # 公司评述 gsps
# 国债回购（204001 = GC001）
c.gzhg_info("204001")               # 回购信息
c.gzhg_quotes("204001", "bpzs")     # 报价张数 bpzs / 回购张数 hgzs / 债券数据 zqsj
# 可交换债 / ABS（冷门，实测样本少）
c.kjhz_finance("127045"); c.kjhz_exchange("127045"); c.kjhz_rate("127045")
c.zczq_profile("146001"); c.zczq_finance("146001"); c.zczq_rating("146001")
# 通用
c.bond_terms("113043", "hstk")      # 条款：回售 hstk / 赎回 shtk / 下修 xztk
c.bond_bulletin("019547")           # 债券公告/资讯
```

**实测**（019547/122000/204001/113043）：概况 1、付息 19、债券数据 30、
企业债评级 11、回购报价 61、条款 1 行等，全部有数据。
`gz_rating`/`gz_finance`/`qyz_review`/`bond_bulletin` 对老债返回 0 行（数据缺失，接口正常）。

## 三、行业家族（hyf10）

`hy` = 通达信行业板块代码（`881319` 半导体），**不是**中文名、不是 `bk` 代码。
可用 `MacClient.get_board_list()` 获取。

```python
HY = "881319"
c.hy_summary(HY, "hqtj")            # 行情统计 / hyzq 行情 / hygy 供应 / zszfb 指数分布
c.hy_profile(HY)                    # 行业介绍
c.hy_news(HY, "hydt")               # 行业动态 hydt / 行业专题 hyzt
c.hy_commentary(HY)                 # 行业评论库
c.hy_members_rank(HY, "cwzkpm")     # 成份股排名：财务指标 cwzkpm / 股本 gsgmpm /
                                    #   估值 gzsppm / 市场表现 scbxpm / 主营收入 zysrpm
c.hy_capital_stats(HY)              # 板块资金统计
c.hy_capital_flow(HY)               # 资金流向
c.hy_fund_holdings(HY)              # 基金持仓
c.hy_analyst_index(HY)              # 分析师指数
c.hy_rating_summary(HY)             # 评级汇总
c.hy_index(HY)                      # 行业指数
c.hy_stage_rise(HY)                 # 阶段涨幅
```

**实测**（半导体）：成份股排名 184~237 行、资金流向 120~185 行、评级汇总 136 行、
分析师指数 148 行、评论库 74 行。`hy_fund_holdings`/`hy_major_holders` 对半导体 0 行。

## 四、期货家族（qhf10）

Entry 在 JS 里写为 `qhf9_*`（不带前缀），由 req.js 自动补 `CWServ.`——
**直接调 `qhf9_*` 会 503**。区分商品（`qhf9_sp_*`）与股指（`qhf9_gz_*`）。

```python
# 持仓报告（必须带日期！cjcc/cjjg 单日；jcgc/ccjj/ykfx 需起止区间）
c.qh_position_report("rb", "cjcc", date="20261020")               # 仓差层次 130 行
c.qh_position_report("rb", "cjjg", date="20261020")               # 持仓结构 53 行
c.qh_position_report("rb", "jcgc", date="20261001", end_date="20261020")  # 会员席位
c.qh_position_report("rb", "ccjj", date="20261001", end_date="20261020")  # 成交均价
c.qh_position_report("rb", "ykfx", date="20261001", end_date="20261020")  # 盈亏分析
c.qh_position_report("IF", "cjcc", date="20261020", index=True)   # 股指 134 行
# 基差价差（002 基差数据 242 行 / 003 价差日期 1167 行）
c.qh_basis_spread("rb", "002", period="1Y")
# 仓单日报（必须带日期，600 行）
c.qh_warehouse_receipt("rb", date="20261020")
# 品种资料
c.qh_variety_info("rb", "pzjj")      # 品种简介
c.qh_variety_info("rb", "hyjj")      # 行业简介 13 行
c.qh_variety_info("rb", "xgzq")      # 相关证券 19 行
# 股指指数资料（code 用 399300）
c.qh_index_info("399300", "zsgk")    # 指数概况 10 行
# 指数估值（code 用 000300，需起止日期）
c.qh_index_valuation("000300", "dtpe", start="20251020", end="20261020")  # 243 行
c.qh_index_valuation("000300", "lspe", start="20251020", end="20261020")  # 729 行
# 成份权重（code 用 399300）
c.qh_weights("399300", "zxcfg")      # 最新成份 1001 行
c.qh_weights("399300", "cfghyfb")    # 成份行业分布 12 行
```

**注意**：指数资料用 `399300`（深证指数代码），指数估值客户端写死 `000300`，
两者不同，勿混用。`qh_inventory`/`lsjg`/`xjfh`/`lscfg`/`cfgqz`/`xwpl`
实测 0 行（数据或参数未确认，方法可用 `params()` 直接试探）。

## 五、测试与验证

- `tests/test_f10_extended.py`：**132 passed**（mock，不触网）
  - 防回归：A 股各板 `normalize_code` 11 项锁定；三家族 Entry/Params 拼装逐项断言
  - 边界：空/非数字/5位/7位/带前缀非数字 → `ProtocolError`；未知 section 抛错
  - 防内存溢出/死循环：分页有界终止、服务端重复返回不累积
  - 分页顺序与去重：跨页顺序拼接、`len==len(set)`
  - 网关路由：`CWServ.qhf9_`/`skef10_hy_`/`skef10_bond_` 命中 page2
- 全量回归：**795 passed**（f10/financial/mac/offline/money_flow/price_rules/client/helpers/mcp 等 16 个文件）

## 六、已知边界

1. **日韩股 F10**：通达信无 jp/kr 家族，结构性缺失（7203 丰田/005930 三星均查不到）。
2. **债券实时行情**：MAC 协议支持（`get_stock_quotes`），但 `normalize_code` 对
   沪深重叠段（110/113/120/122/124）无法纯代码推断市场，建议显式 `sh`/`sz` 前缀。
3. **港股公告原文 URL**：通达信未存（hkexnews 独立接口），美股公告 `mg_announcements`
   的 `N003` 字段是 SEC EDGAR 公网地址（访问需带 User-Agent，否则 403）。
4. **期货冷门 Entry**：库存报告/历史价格/现金分红等实测 0 行，参数形式可能因品种而异。
