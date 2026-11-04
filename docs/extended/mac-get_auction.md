---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 集合竞价

读取集合竞价过程中的价格、匹配量及带符号未匹配量。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x123D | `list[AuctionItem]` |

## 调用签名

```text
MacClient.get_auction(market: int, code: str) -> list[AuctionItem]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | MAC 市场编号；A 股常用 0=深、1=沪。板块等品种请沿用枚举/列表返回的市场号，不与 ExMarket 混用。 |
| `code` | `str` | 必填 | 服务器证券/合约/指标代码；保留前导零，大小写遵循标的列表。A 股传六位裸代码。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient

with MacClient() as client:
    result = client.get_auction(0, "000001")
    print(result)
```

## 分页、单位与限制

时间按原始当日秒数解析；matched 是虚拟匹配量，unmatched 为带符号未匹配量，保留符号。是过程快照，不是已完成的真实逐笔成交。当前无日期参数、无分页；不要把该通道数量未经核对直接混入标准 0x056A 的手数口径。

## 返回字段

### AuctionItem

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `time` | `time` | 当日时间，无日期与时区；MacSymbolInfo 为完整 datetime。 |
| `price` | `float` | 当前解析得到的价格；EX 成交 price 是整数原值，MAC price 是浮点值。 |
| `matched` | `int` | 虚拟匹配量原值，不代表已完成成交。 |
| `unmatched` | `int` | 带符号的未匹配量原值；保留符号。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
