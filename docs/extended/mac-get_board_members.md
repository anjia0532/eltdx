---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 板块成分股报价

按用户板块代码读取成分证券的排序报价。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x122C | `list[MacQuoteField]` |

## 调用签名

```text
MacClient.get_board_members(board_symbol: str, count: int=100000, sort_type: SortType=SortType.CHANGE_PCT, sort_order: SortOrder=SortOrder.DESC, fields: Fields=PresetField.COMMON, exclude_flags: list[FilterType] | None=None) -> list[MacQuoteField]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `board_symbol` | `str` | 必填 | 用户看到的板块代码字符串，例如 881001；客户端先用 convert_board_code 转为请求编号。 |
| `count` | `int` | `100000` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |
| `sort_type` | `SortType` | `SortType.CHANGE_PCT` | 服务端排序字段，使用 SortType 枚举。 |
| `sort_order` | `SortOrder` | `SortOrder.DESC` | 服务端排序方向：NONE=不指定、DESC=降序、ASC=升序。 |
| `fields` | `Fields` | `PresetField.COMMON` | FieldBit、PresetField 或 FieldSelection 字段集合；仅请求的字段进入 fields 字典，默认集合见说明。 |
| `exclude_flags` | `list[FilterType] \| None` | `None` | FilterType 列表，按位组合以排除 ST、科创板等分类；None 表示不增加过滤。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient

with MacClient() as client:
    result = client.get_board_members("881001", count=100)
    print(result)
```

## 分页、单位与限制

最多 80 条/页，count 为总数；0x122C 的字段位只支持 0..127，含更高位的字段集合会抛 ValueError；服务端排序，客户端顺序拼接。board_symbol 会经 convert_board_code 转换：88xxxx、399xxx、899xxx、USxxxx、HKxxxx 等按各自规则编码，不应把展示代码直接当原始请求编号。完整转换表见枚举页。

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
