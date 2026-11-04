---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC-EX 成交明细

按市场路由到 MAC 成交或港股专用 EX 成交，返回统一模型。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacExClient | 7727 | 0x122F / 0x23FC / 0x2406 | `list[MacTransaction]` |

## 调用签名

```text
MacExClient.goods_transaction(market: int, code: str, query_date: date | None=None, start: int=0, count: int=2000) -> list[MacTransaction]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | 扩展市场号 ExMarket，例如 31=港股主板、33=开放式基金、47=中金所期货、74=美股；不是标准 A 股 0/1 市场号。 |
| `code` | `str` | 必填 | 服务器证券/合约/指标代码；保留前导零，大小写遵循标的列表。A 股传六位裸代码。 |
| `query_date` | `date \| None` | `None` | datetime.date 对象或 None；不同于 MacClient 的整数 date 参数。None 表示当前数据。 |
| `start` | `int` | `0` | 记录起始偏移，通常从 0 开始；偏移方向与分页范围见本页说明。 |
| `count` | `int` | `2000` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |

## 使用示例

示例代码用于展示调用方式。

```python
from datetime import date
from eltdx.ex import MacExClient

with MacExClient() as client:
    result = client.goods_transaction(31, "00700", query_date=date(2026, 10, 29), count=100)
    print(result)
```

## 分页、单位与限制

港股股票类市场集合为 27、31、48、49、71、98；这些市场当日走 0x23FC，指定日期走 0x2406，每页最多 1800 条，自动取到 count 或短/空页。港股 price /1000 为港元，trade_count 填 0 表示源协议没有笔数，不是该记录没有成交。

其余市场直接发一次 0x122F，不自动分页；count 默认 2000 不保证服务器足额返回。不能把 A 股三秒聚合的观察直接推广到期货或美股。港股衍生品 23..26 不属于上述路由集合。

## 返回字段

### MacTransaction

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `time` | `time` | 当日时间，无日期与时区；MacSymbolInfo 为完整 datetime。 |
| `price` | `float` | 当前解析得到的价格；EX 成交 price 是整数原值，MAC price 是浮点值。 |
| `vol` | `int` | 服务端数量原值；不同市场和品种的数量单位需单独核对。 |
| `trade_count` | `int` | 服务端成交笔数；聚合记录可 >1，港股 EX 转换模型固定为 0（未提供）。 |
| `bs_flag` | `int` | 原始买卖/状态值；MAC 常见 0=买、1=卖、2=中性、5=盘后；跨市场需核对。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/mac_client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
