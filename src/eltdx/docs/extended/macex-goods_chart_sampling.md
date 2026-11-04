---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC-EX 分时缩略采样

读取扩展品种的小走势图价格点。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacExClient | 7727 | 0x254D | `list[float]` |

## 调用签名

```text
MacExClient.goods_chart_sampling(market: int, code: str) -> list[float]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | 扩展市场号 ExMarket，例如 31=港股主板、33=开放式基金、47=中金所期货、74=美股；不是标准 A 股 0/1 市场号。 |
| `code` | `str` | 必填 | 服务器证券/合约/指标代码；保留前导零，大小写遵循标的列表。A 股传六位裸代码。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import MacExClient

with MacExClient() as client:
    result = client.goods_chart_sampling(74, "AAPL")
    print(result)
```

## 分页、单位与限制

返回 list[float]，通常约 240 个点，以响应为准。没有时间或成交量，不能用数组位置还原精确交易事件。

## 返回字段

每项是原始价格浮点数，列表不携带时间轴。

## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/mac_client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
