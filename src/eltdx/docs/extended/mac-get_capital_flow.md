---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 个股资金流

读取 Stock_ZJLX 数据并整理为资金流模型。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x1218 / head_flag=2 | `CapitalFlowData \| None` |

## 调用签名

```text
MacClient.get_capital_flow(market: int, code: str) -> CapitalFlowData | None
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
    result = client.get_capital_flow(0, "000001")
    print(result)
```

## 分页、单位与限制

无有效数据返回 None。当前映射混合口径：main_*、small_* 来自第一组当日数据；mid_net、large_net 来自第二组五日数据，而非当日中大单净额。date 当前固定空字符串；mid_in、mid_out、large_in、large_out 固定 0，表示没有映射，不能据此判断真实流入为零。该结果不是标准 money_flow.history 的逐日历史表；金额单位在本页未做新的跨源校准，按原始值保留。

## 返回字段

### CapitalFlowData

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `date` | `str` | 交易日期；CapitalFlowData 当前固定为空字符串。 |
| `main_in` | `float` | 当日主力流入原值。 |
| `main_out` | `float` | 当日主力流出原值。 |
| `main_net` | `float` | main_in-main_out。 |
| `small_in` | `float` | 当日散户流入原值。 |
| `small_out` | `float` | 当日散户流出原值。 |
| `small_net` | `float` | small_in-small_out。 |
| `mid_in` | `float` | 当前映射固定 0，未提供此字段。 |
| `mid_out` | `float` | 当前映射固定 0，未提供此字段。 |
| `mid_net` | `float` | 当前从第二组数据取五日值，不是当日中单净额。 |
| `large_in` | `float` | 当前映射固定 0，未提供此字段。 |
| `large_out` | `float` | 当前映射固定 0，未提供此字段。 |
| `large_net` | `float` | 当前从第二组数据取五日值，不是当日大单净额。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
