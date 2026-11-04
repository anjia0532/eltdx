---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC-EX 商品数量

获取全市场或指定市场的商品数量。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacExClient | 7727 | 0x23F0 / 0x2562 / 0x23F5 | `int` |

## 调用签名

```text
MacExClient.goods_count(market: int | None=None) -> int
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int \| None` | `None` | 扩展市场号 ExMarket，例如 31=港股主板、33=开放式基金、47=中金所期货、74=美股；不是标准 A 股 0/1 市场号。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import MacExClient

with MacExClient() as client:
    result = client.goods_count(33)
    print(result)
```

## 分页、单位与限制

market=None 直接用 EX 0x23F0；给定 market 时先试 0x2562 的 total，为 0 则通过 EX 元数据定位市场上下界后相减。回退依赖全表按市场号有序，计数不代表这些商品都服务实时行情。

## 返回字段

返回单个整数；其计数范围见上面的说明。

## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/mac_client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
