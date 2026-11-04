---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC-EX 港股全量成交

为港股股票类市场逐页读取当日或指定日成交。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacExClient | 7727 | 0x23FC / 0x2406 | `list[MacTransaction]` |

## 调用签名

```text
MacExClient.goods_transaction_all(market: int, code: str, query_date: date | None=None) -> list[MacTransaction]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | 扩展市场号 ExMarket，例如 31=港股主板、33=开放式基金、47=中金所期货、74=美股；不是标准 A 股 0/1 市场号。 |
| `code` | `str` | 必填 | 服务器证券/合约/指标代码；保留前导零，大小写遵循标的列表。A 股传六位裸代码。 |
| `query_date` | `date \| None` | `None` | datetime.date 对象或 None；不同于 MacClient 的整数 date 参数。None 表示当前数据。 |

## 使用示例

示例代码用于展示调用方式。

```python
from datetime import date
from eltdx.ex import MacExClient

with MacExClient() as client:
    result = client.goods_transaction_all(31, "00700", query_date=date(2026, 10, 29))
    print(result)
```

## 分页、单位与限制

只接受 27、31、48、49、71、98，其他市场抛 ValueError。每页 1800 条，最多 50 页即 90000 条；达到安全上限也会返回当前累计列表，因此名称“全量”不代表任何成交量下都无限取完。盘中分页会受新增记录影响。港股 price 已换算港元；trade_count 为未提供值 0。

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
