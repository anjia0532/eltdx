# 宏观指标（GDP/CPI/PMI…）取数方案与封装

> 结论先行：**能取到，走扩展行情（MacExClient，7727），不走 JS 缓存**。
> 通达信「宏观数据」页是**客户端原生页面**（`T0002/cloud_dax/HGSJ.sp`，
> GPType=88），不产生 web JS 缓存；数据源是市场 38 的特殊证券。

## 一、取证过程

1. **JS 缓存无宏观页**：`T0002/tmp/Code Cache/js/*_0` 里只有 `kggx/tk_hy.js`
   （行业图库，Entry `CWServ.cfg_tk_gethy_cfg`），无任何宏观数据页面 URL——
   因为宏观页不是 web 页。
2. **客户端布局定义**：`T0002/cloud_dax/HGSJ.sp`（GBK 编码）显示
   「宏观数据」页 = 宏观指标表格（HQGRID_UNIT）+ K 线（FXT_UNIT）+ 宏观资讯
   （BIGDATA_UNIT，`CfgName=func_cjrl101`）；指标编码 `GPSetCode_Code1=38_1_GDP`，
   即**市场 38 + 类别 1 + GDP**。
3. **eltdx 枚举已有市场 38**：`ExMarket.MACRO_INDICATOR = 38`
   （`ex/enums.py`、`mac/enums.py`）。
4. **MAC 报价协议不支持**：`MacClient.get_stock_quotes([(38, 'GDP')])` 返回空
   （7709 不服务市场 38）。
5. **扩展行情支持**：`MacExClient.goods_list(38)` → **217 个指标**；
   `goods_quotes([(38, '1_GDP')])` → 名称+数值；
   `goods_kline(38, '1_GDP', Period.YEARLY)` → 历史序列。

## 二、封装（`MacExClient`，市场 38）

```python
from eltdx.ex.mac_client import MacExClient
from eltdx.mac.enums import Period

with MacExClient("116.205.135.205", 7727, 10.0) as c:
    # 1) 全部指标（217 个，9 类）
    items = c.macro_indicators()
    # 2) 最新值（裸代码自动补类别）
    for f in c.macro_quotes(["GDP", "CPI", "PPI", "PMI", "M2", "BDI"]):
        print(f.code, f.name, f.fields["close"], f.fields["pre_close"])
    # 3) 历史序列（period 与发布频率匹配）
    gdp = c.macro_kline("GDP", Period.YEARLY)     # 36 根（1989-2025）
    cpi = c.macro_kline("CPI", Period.MONTHLY)    # 393 根
    pmi = c.macro_kline("PMI", Period.MONTHLY)    # 261 根
```

### 方法清单

| 方法 | 说明 |
|---|---|
| `macro_indicators()` | 全部指标（`goods_list(38)` 包装，实例缓存） |
| `macro_quotes(codes)` | 最新值；`codes` 支持 `1_GDP` 或裸 `GDP`；空列表不触网 |
| `macro_kline(code, period)` | 历史序列；默认 `MONTHLY` |
| `MACRO_CATEGORIES` | 类别 1~9 → 中文名（国民经济/物价/景气/对外经济/货币金融/房地产与其他/证券市场/美国经济/利率与回购） |

### 代码规范化规则（`_macro_code`）

- 含 `_`（如 `1_GDP`）→ 原样返回
- 裸代码（`GDP`）→ 在全部指标中按后缀匹配：唯一命中直接用；**多命中抛
  `ValueError` 列出候选**（如 `XAU` 若同属多类别）；无命中抛 `ProtocolError`
- 缓存为空时自动拉一次指标列表（之后命中缓存）

## 三、实测数据（2026-10-22）

| 代码 | 名称 | 最新值 | 前值 | 历史 |
|---|---|---|---|---|
| `1_GDP` | 年度国内生产总值 | 1401879.25（亿元） | 1348066.25 | YEARLY 36 根 |
| `2_CPI` | 居民消费价格指数 | 100.90 | 100.80 | MONTHLY 393 根 |
| `2_PPI` | 工业出厂价格指数 | 105.00 | 103.80 | MONTHLY |
| `3_PMI` | 制造业采购指数 | 50.10 | 49.80 | MONTHLY 261 根 |
| `5_M2` | 广义货币供应量 | 3596289.75 | 3568083.50 | MONTHLY |
| `5_BDI` | 波罗的海BDI指数 | 2680.00 | 2593.00 | DAILY |

## 四、217 个指标分类

| 类别 | 名称 | 数量 | 代表指标 |
|---|---|---|---|
| 1 | 国民经济 | 3 | GDP、GDPI、MSR |
| 2 | 物价 | 5 | CPI、PPI、CGPI、PPCI、PPPI |
| 3 | 景气指数 | 12 | PMI、PMIN、PMIF、BCI、CCI、CSI |
| 4 | 对外经济 | 8 | TIE、MEI、MEU、MII、MIU、DEXW、GEXW、CBEC |
| 5 | 货币金融 | 53 | M0/M1/M2、SHIBOR、SHR*/SHS*、GOLD、CNT*Y 国债利率、RMBUS |
| 6 | 房地产与其他 | 12 | BTCUSD、ETHUSD、FDI、QYEARN、VGDP |
| 7 | 证券市场 | 18 | BMSETF、SETF、TETF、AMO 等基金数据 |
| 8 | 美国经济 | 30 | AAGDP、ACPI、APMI、EFFR、SOFR、ICSA、USDEBT |
| 9 | 利率与回购 | 76 | 990001~990033（中债收益率曲线）、R001/R007 回购、MLF、SLF、OMOR |

完整清单：`tmp_f10/macro_indicators.json`。

## 五、注意事项

1. **主机**：`MacExClient` 默认 `MAC_EX_HOSTS`（116.205.135.205 / 121.37.232.167）；
   `ExTdxClient` 的 `DEFAULT_EX_HOSTS`（16 台云主机）当前全部拒连，
   `from_best_host()` 并发探测会明显变慢，建议直接指定主机。
2. **无成交量**：宏观指标 `vol`/`amount` 恒 0（非交易品种）。
3. **更新频率**：按报告期更新（月/季/年），`pre_close` 是上一报告期值；
   K 线 `period` 应与发布频率匹配（GDP→YEARLY/QUARTERLY，CPI/PMI→MONTHLY，
   利率→DAILY）。
4. **类别 9 的 990xxx**：中债国债收益率曲线（1Y/3Y/5Y/10Y/30Y 等），
   代码为数字，`macro_kline("990001", Period.DAILY)` 可取历史利率。

## 六、测试

`tests/test_macro_indicators.py`：**13 passed**（mock，不触网）

- 防回归：市场 38 枚举值、类别映射 1~9
- 边界：完整代码/裸代码/歧义（ValueError 列候选）/未知（ProtocolError）/空列表
- 缓存：`_macro_code` 复用指标列表，只拉一次
- 路由：`macro_indicators`/`macro_quotes`/`macro_kline` 全部锁市场 38

核心回归套件（含 macro/f10/financial/mac/offline/money_flow/price_rules/ex_failover）：
**593 passed**。
