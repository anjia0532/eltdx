---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 市场盘口异动

读取市场异动事件及解析后的说明文字。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x1237 | `list[UnusualItem]` |

## 调用签名

```text
MacClient.get_unusual(market: int, start: int=0, count: int=0) -> list[UnusualItem]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | MAC 市场编号；A 股常用 0=深、1=沪。板块等品种请沿用枚举/列表返回的市场号，不与 ExMarket 混用。 |
| `start` | `int` | `0` | 记录起始偏移，通常从 0 开始；偏移方向与分页范围见本页说明。 |
| `count` | `int` | `0` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient

with MacClient() as client:
    result = client.get_unusual(0, start=0, count=100)
    print(result)
```

## 分页、单位与限制

count=0 会转换为 600；这是单页请求，高层不自动取全。desc/value 由解析器根据 unusual_type 整理；value 可含百分号、倍数或组合文本，不是统一数值。未知类型保留编号，不应当作漏数或零值。

## 返回字段

### UnusualItem

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `index` | `int` | 协议序号/索引；商品索引不是永久证券 ID。 |
| `market` | `int` | 市场编号，按当前协议的市场表解释。 |
| `code` | `str` | 证券/合约代码字符串，保留前导零。 |
| `name` | `str` | 名称文本；GoodsItem 的特殊语义见该模型。 |
| `time` | `time` | 当日时间，无日期与时区；MacSymbolInfo 为完整 datetime。 |
| `desc` | `str` | 描述文本。 |
| `value` | `str` | 已格式化异动值，可能含 %、倍数或组合文本。 |
| `unusual_type` | `int` | 异动类型原始编号。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
