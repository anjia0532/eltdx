---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# EX 分类报价列表

分页读取扩展市场分类报价。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| ExTdxClient | 7727 | 0x2400 | `list[OrderedDict[str, object]]` |

## 调用签名

```text
ExTdxClient.get_instrument_quote_list(market: int, category: int, start: int=0, count: int=80) -> list[OrderedDict[str, object]]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | 扩展市场号 ExMarket，例如 31=港股主板、33=开放式基金、47=中金所期货、74=美股；不是标准 A 股 0/1 市场号。 |
| `category` | `int` | 必填 | 行情解析类别，仅接受 2（港股）或 3（期货）；其他值抛 ValueError。 |
| `start` | `int` | `0` | 记录起始偏移，通常从 0 开始；偏移方向与分页范围见本页说明。 |
| `count` | `int` | `80` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import ExTdxClient

with ExTdxClient() as client:
    result = client.get_instrument_quote_list(47, category=3, count=20)
    print(result)
```

## 分页、单位与限制

本方法使用传统 EX 请求帧。仓库此前 2026-10 的默认主机实测中，元数据命令可部分使用，而本类行情命令多为超时或断开；这是历史样本，不是永久保证。支持的命令需逐台核实，TCP 连通或总数可查不代表行情可查。可对照 MAC-EX 对应能力，但它使用不同请求协议。

category 仅允许 2（港股）与 3（期货），决定响应解析布局；请求体并不编码这个 category。返回 OrderedDict 列表，字段为兼容的拼音键，保留各类别差异，不是 MacQuoteField。单页，无自动补齐 count。

## 返回字段

| 键 / 键组 | 含义 |
| --- | --- |
| market / code | 市场及商品代码。 |
| BiShu / KaiCang / ChiCangLiang | 期货笔数、开仓和持仓。 |
| ZuoJie / ZuoShou | 期货昨结/港股昨收，按解析类别出现。 |
| JinKai / ZuiGao / ZuiDi | 开盘、最高、最低。 |
| XianJia / MaiChu / MaiRuJia | 港股最新价、期货相关报价字段；保留各类别键。 |
| ZongLiang / XianLiang / ZongJinE | 总量、现量、金额原值。 |
| NeiPan / WaiPan / Nei / Wai | 期货或港股各自命名的内外盘字段。 |
| MaiRuJia1..5 / MaiChuJia1..5 | 港股五档买卖价。 |
| MaiRuLiang1..5 / MaiChuLiang1..5 | 港股五档买卖数量。 |
| MaiRuLiang / MaiChuJia / MaiChuLiang | 期货买量、卖价与卖量。 |
| HuoYueDu | 港股活跃度。 |

## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
