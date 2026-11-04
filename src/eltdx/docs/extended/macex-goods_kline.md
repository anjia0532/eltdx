---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC-EX 扩展市场K线

读取基金、外盘、期货等扩展品种的 K 线。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacExClient | 7727 | 0x122E | `list[MacBar]` |

## 调用签名

```text
MacExClient.goods_kline(market: int, code: str, period: Period=Period.DAILY, start: int=0, count: int=800, adjust: Adjust=Adjust.NONE) -> list[MacBar]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | 扩展市场号 ExMarket，例如 31=港股主板、33=开放式基金、47=中金所期货、74=美股；不是标准 A 股 0/1 市场号。 |
| `code` | `str` | 必填 | 服务器证券/合约/指标代码；保留前导零，大小写遵循标的列表。A 股传六位裸代码。 |
| `period` | `Period` | `Period.DAILY` | Period 枚举；常用 DAILY、MIN_1、MIN_5、MONTHLY 等。枚举存在不代表全部服务器都有对应数据。 |
| `start` | `int` | `0` | 记录起始偏移，通常从 0 开始；偏移方向与分页范围见本页说明。 |
| `count` | `int` | `800` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |
| `adjust` | `Adjust` | `Adjust.NONE` | Adjust.NONE=不复权、QFQ=前复权、HFQ=后复权；服务端是否支持取决于品种。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import MacExClient
from eltdx.mac import Period

with MacExClient() as client:
    result = client.goods_kline(74, "AAPL", period=Period.DAILY, count=100)
    print(result)
```

## 分页、单位与限制

单次命令，无 MacClient 的每页 700 条自动翻页、XDXR 本地复权兜底或 bar_time 参数。start=0 最新段，实际条数和复权支持随主机/品种变化。价格、成交量、金额保持品种口径；基金/宏观记录不是股票交易 bar。

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

签名与行为依据当前仓库 `src/eltdx/ex/mac_client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
