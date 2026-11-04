---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 复权K线

读取多周期 K 线，支持服务端复权和自动分页。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x122E | `list[MacBar]` |

## 调用签名

```text
MacClient.get_stock_kline(market: int, code: str, period: Period=Period.DAILY, start: int=0, count: int=800, times: int=1, adjust: Adjust=Adjust.NONE, *, bar_time: str=BAR_TIME_START) -> list[MacBar]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | MAC 市场编号；A 股常用 0=深、1=沪。板块等品种请沿用枚举/列表返回的市场号，不与 ExMarket 混用。 |
| `code` | `str` | 必填 | 服务器证券/合约/指标代码；保留前导零，大小写遵循标的列表。A 股传六位裸代码。 |
| `period` | `Period` | `Period.DAILY` | Period 枚举；常用 DAILY、MIN_1、MIN_5、MONTHLY 等。枚举存在不代表全部服务器都有对应数据。 |
| `start` | `int` | `0` | 记录起始偏移，通常从 0 开始；偏移方向与分页范围见本页说明。 |
| `count` | `int` | `800` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |
| `times` | `int` | `1` | 周期倍数，配合 Period.MINS / DAYS / SECONDS 使用；常规周期保持 1。 |
| `adjust` | `Adjust` | `Adjust.NONE` | Adjust.NONE=不复权、QFQ=前复权、HFQ=后复权；服务端是否支持取决于品种。 |
| `bar_time` | `str` | `BAR_TIME_START` | "start" 保留起点时间；"end" 对已知分钟周期移到右端点。日线不移动；范围接口另有限制。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient, Period, Adjust

with MacClient() as client:
    result = client.get_stock_kline(1, "600519", period=Period.MIN_5, count=100, adjust=Adjust.NONE, bar_time="end")
    print(result)
```

## 分页、单位与限制

start=0 为最新一段；每页最多 700 条，高层将更旧的页前插，最终按旧到新返回。count 是总条数。bar_time="end" 只移动已知分钟周期。Period.SECONDS 是协议可表达的周期，不承诺所有主机服务秒 K。QFQ 结果出现非正/非有限价格时会再查不复权数据；仅当配置 xdxr_provider 且重算有效时替换，否则保留原始复权结果，不保证兜底成功。

## 返回字段

### MacBar

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `datetime` | `datetime` | 服务器日期时间，无时区；时间起止口径见调用参数。 |
| `open` | `float` | 开盘/周期起值。 |
| `high` | `float` | 区间最高值。 |
| `low` | `float` | 区间最低值。 |
| `close` | `float` | 最新/周期结束值；宏观为报告值、基金可能为净值。 |
| `vol` | `float` | 服务端数量原值；不同市场和品种的数量单位需单独核对。 |
| `amount` | `float` | 服务端金额字段；EX K 线的特殊映射见对应页面。 |
| `float_shares` | `float` | 协议流通量字段，保持原值，未统一股/万股口径。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
