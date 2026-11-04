---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC-EX 批量报价与净值

按市场和代码批量读取基金净值或外盘行情。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacExClient | 7727 | 0x122B | `list[MacQuoteField]` |

## 调用签名

```text
MacExClient.goods_quotes(stocks: list[tuple[int, str]], fields: Any=None) -> list[MacQuoteField]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `stocks` | `list[tuple[int, str]]` | 必填 | [(market, code), ...] 元组列表；不是 sh600519 等完整代码字符串列表。 |
| `fields` | `Any` | `None` | FieldBit、PresetField 或 FieldSelection 字段集合；仅请求的字段进入 fields 字典，默认集合见说明。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import MacExClient

with MacExClient() as client:
    result = client.goods_quotes([(33, "016947"), (74, "AAPL")])
    print(result)
```

## 分页、单位与限制

默认只有 pre_close/open/high/low/close/vol/amount 七个基础字段；可传 FieldBit/PresetField 扩展。单次请求，不自动拆批，建议每次不超过 80 项。基金 close 可能为净值，不是股票成交价；不能把所有市场的 vol、amount 强行按 A 股股数和人民币解释。

## 返回字段

### MacQuoteField

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `market` | `int` | 市场编号，按当前协议的市场表解释。 |
| `code` | `str` | 证券/合约代码字符串，保留前导零。 |
| `name` | `str` | 名称文本；GoodsItem 的特殊语义见该模型。 |
| `fields` | `dict[str, Any]` | 按请求位图解析的动态字典；键名为 FieldBit.field_name。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/mac_client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
