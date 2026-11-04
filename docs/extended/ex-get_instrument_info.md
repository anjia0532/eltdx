---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# EX 商品信息

分页读取全局商品元数据，包括市场、代码、名称和类别。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| ExTdxClient | 7727 | 0x23F5 | `list[ExInstrumentInfo]` |

## 调用签名

```text
ExTdxClient.get_instrument_info(start: int, count: int=100) -> list[ExInstrumentInfo]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `start` | `int` | 必填 | 记录起始偏移，通常从 0 开始；偏移方向与分页范围见本页说明。 |
| `count` | `int` | `100` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import ExTdxClient

with ExTdxClient() as client:
    result = client.get_instrument_info(start=0, count=100)
    print(result)
```

## 分页、单位与限制

start 是全市场偏移，不是某市场内偏移；高层单页返回。循环时 start += len(rows)，空页或达到总数停止。返回列表可能跨市场；需要单市场列表可改用 MacExClient.instruments。

## 返回字段

### ExInstrumentInfo

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `category` | `int` | 商品/市场类别原始编号，与 K 线周期 category 并非同一概念。 |
| `market` | `int` | 市场编号，按当前协议的市场表解释。 |
| `code` | `str` | 证券/合约代码字符串，保留前导零。 |
| `name` | `str` | 名称文本；GoodsItem 的特殊语义见该模型。 |
| `desc` | `str` | 描述文本。 |
| `_raw` | `bytes` | 本条原始记录字节，供复核；JSON 展示时需自行编码。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
