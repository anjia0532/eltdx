---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 批量报价

用字段位图一次读取多只证券的报价和扩展指标。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x122B | `list[MacQuoteField]` |

## 调用签名

```text
MacClient.get_stock_quotes(stocks: list[tuple[int, str]], fields: Fields | None=None) -> list[MacQuoteField]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `stocks` | `list[tuple[int, str]]` | 必填 | [(market, code), ...] 元组列表；不是 sh600519 等完整代码字符串列表。 |
| `fields` | `Fields \| None` | `None` | FieldBit、PresetField 或 FieldSelection 字段集合；仅请求的字段进入 fields 字典，默认集合见说明。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient, PresetField, FieldBit

with MacClient() as client:
    result = client.get_stock_quotes([(0, "000001"), (1, "600519")], fields=PresetField.BASIC + FieldBit.AMOUNT)
    print(result)
```

## 分页、单位与限制

默认 PresetField.COMMON；单次按最多 80 只设计，高层不会自动拆分 stocks。空列表在命令构造时抛 ValueError。fields 只包含已选且服务器实际返回的字段，缺键与值为 0 含义不同。完整位图、类型与中文说明见[枚举与字段位图](枚举与字段位图.md)。

## 返回字段

### MacQuoteField

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `market` | `int` | 市场编号，按当前协议的市场表解释。 |
| `code` | `str` | 证券/合约代码字符串，保留前导零。 |
| `name` | `str` | 名称文本；GoodsItem 的特殊语义见该模型。 |
| `fields` | `dict[str, Any]` | 按请求位图解析的动态字典；键名为 FieldBit.field_name。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
