---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 板块列表

枚举板块，并附带板块和领涨证券的价格信息。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x1231 | `list[BoardInfo]` |

## 调用签名

```text
MacClient.get_board_list(board_type: BoardType=BoardType.ALL, count: int=10000) -> list[BoardInfo]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `board_type` | `BoardType` | `BoardType.ALL` | BoardType 枚举，HY=一级行业、GN=概念、ALL=全部；完整取值见枚举页。 |
| `count` | `int` | `10000` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient, BoardType

with MacClient() as client:
    result = client.get_board_list(BoardType.HY, count=100)
    print(result)
```

## 分页、单位与限制

count 为总数，高层按 150 条分页；空页、短页或足额停止。BoardInfo 的 symbol_* 是领涨证券，不是当前板块自身字段。rise_speed 是服务端涨速字段，涨跌幅可用 (price/pre_close-1)*100 计算，分母为 0 时另行处理。

## 返回字段

### BoardInfo

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `market` | `int` | 市场编号，按当前协议的市场表解释。 |
| `code` | `str` | 证券/合约代码字符串，保留前导零。 |
| `name` | `str` | 名称文本；GoodsItem 的特殊语义见该模型。 |
| `price` | `float` | 当前解析得到的价格；EX 成交 price 是整数原值，MAC price 是浮点值。 |
| `rise_speed` | `float` | 板块涨速原值，不是计算后的日涨幅。 |
| `pre_close` | `float` | 前收/前参考值；基金及宏观指标按各自业务口径。 |
| `symbol_market` | `int` | 领涨证券的市场。 |
| `symbol_code` | `str` | 领涨证券代码。 |
| `symbol_name` | `str` | 领涨证券名称。 |
| `symbol_price` | `float` | 领涨证券最新价格。 |
| `symbol_rise_speed` | `float` | 领涨证券涨速。 |
| `symbol_pre_close` | `float` | 领涨证券前收。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
