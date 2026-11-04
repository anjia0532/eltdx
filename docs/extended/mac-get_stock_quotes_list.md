---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 分类排行

按市场分类读取服务器排序后的报价列表。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x122C | `list[MacQuoteField]` |

## 调用签名

```text
MacClient.get_stock_quotes_list(category: Category, start: int=0, count: int=80, sort_type: SortType=SortType.CHANGE_PCT, sort_order: SortOrder=SortOrder.DESC, exclude_flags: list[FilterType] | None=None, fields: Fields | None=None) -> list[MacQuoteField]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `category` | `Category` | 必填 | Category 枚举，如 A、SH、SZ、KCB；与 EX 周期 category、EX 行情类别不同。 |
| `start` | `int` | `0` | 记录起始偏移，通常从 0 开始；偏移方向与分页范围见本页说明。 |
| `count` | `int` | `80` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |
| `sort_type` | `SortType` | `SortType.CHANGE_PCT` | 服务端排序字段，使用 SortType 枚举。 |
| `sort_order` | `SortOrder` | `SortOrder.DESC` | 服务端排序方向：NONE=不指定、DESC=降序、ASC=升序。 |
| `exclude_flags` | `list[FilterType] \| None` | `None` | FilterType 列表，按位组合以排除 ST、科创板等分类；None 表示不增加过滤。 |
| `fields` | `Fields \| None` | `None` | FieldBit、PresetField 或 FieldSelection 字段集合；仅请求的字段进入 fields 字典，默认集合见说明。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient, Category, SortType

with MacClient() as client:
    result = client.get_stock_quotes_list(Category.A, count=100, sort_type=SortType.CHANGE_PCT)
    print(result)
```

## 分页、单位与限制

默认字段为 PresetField.BASIC + PresetField.VOLUME，默认按涨幅降序。0x122C 的字段位只支持 0..127，高位字段会抛 ValueError。每页最多 80 条，高层按剩余数量分页并顺序拼接；遇空页、短页或足额停止。排行会随行情变动，跨页不是同一时刻的快照，可能重复或遗漏。

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
