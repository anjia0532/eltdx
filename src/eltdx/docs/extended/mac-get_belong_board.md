---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 个股所属板块

反向查询一只证券所属的板块。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x1218 / head_flag=1 | `list[BelongBoardInfo]` |

## 调用签名

```text
MacClient.get_belong_board(market: int, code: str) -> list[BelongBoardInfo]
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
    result = client.get_belong_board(0, "000001")
    print(result)
```

## 分页、单位与限制

请求名为 Stock_GLHQ；同样的 0x1218 还用于资金流，但 head_flag 和请求名不同。返回列表，无高层分页。缺失的 close/pre_close 当前填 0，不代表板块价格实际为 0。

## 返回字段

### BelongBoardInfo

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `board_type` | `int` | 板块类型编号。 |
| `market` | `int` | 市场编号，按当前协议的市场表解释。 |
| `board_code` | `str` | 板块展示代码。 |
| `board_name` | `str` | 板块中文名称。 |
| `close` | `float` | 最新/周期结束值；宏观为报告值、基金可能为净值。 |
| `pre_close` | `float` | 前收/前参考值；基金及宏观指标按各自业务口径。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
