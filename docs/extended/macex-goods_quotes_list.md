---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC-EX 列表报价

枚举一段商品代码后读取基础报价。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacExClient | 7727 | 0x2562 / 0x23F5 + 0x122B | `list[MacQuoteField]` |

## 调用签名

```text
MacExClient.goods_quotes_list(market: int, start: int=0, count: int=100, sort_type: SortType=SortType.CODE, sort_order: SortOrder=SortOrder.NONE) -> list[MacQuoteField]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | 扩展市场号 ExMarket，例如 31=港股主板、33=开放式基金、47=中金所期货、74=美股；不是标准 A 股 0/1 市场号。 |
| `start` | `int` | `0` | 记录起始偏移，通常从 0 开始；偏移方向与分页范围见本页说明。 |
| `count` | `int` | `100` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |
| `sort_type` | `SortType` | `SortType.CODE` | SortType 排序字段；MAC-EX 排序报价的该参数目前仅预留，不生效。 |
| `sort_order` | `SortOrder` | `SortOrder.NONE` | SortOrder.NONE / DESC / ASC；MAC-EX 排序报价的该参数目前仅预留，不生效。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import MacExClient

with MacExClient() as client:
    result = client.goods_quotes_list(33, start=0, count=20)
    print(result)
```

## 分页、单位与限制

当前最多取 min(count,80) 个商品，不自动把 count>80 的请求补齐。sort_type、sort_order 接受参数但完全不参与请求和排序，名称不能理解为已实现涨幅排行榜。需要排序请自行明确字段并对完整所需样本排序。

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
