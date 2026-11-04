---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 个股特征快照

读取证券身份、行情时间、价格、成交与内外盘等简要特征。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x122A | `MacSymbolInfo` |

## 调用签名

```text
MacClient.get_symbol_info(market: int, code: str) -> MacSymbolInfo
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
    result = client.get_symbol_info(1, "600519")
    print(result)
```

## 分页、单位与限制

单次查询，不是历史序列。time 从服务端日期与 HHMMSS 组合，无时区。返回数量和换手字段保持本协议口径；未经过标准 7709 TdxClient 的价格/手数统一处理。

## 返回字段

### MacSymbolInfo

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `market` | `int` | 市场编号，按当前协议的市场表解释。 |
| `code` | `str` | 证券/合约代码字符串，保留前导零。 |
| `name` | `str` | 名称文本；GoodsItem 的特殊语义见该模型。 |
| `time` | `datetime \| None` | 服务器完整日期时间或 None，无时区。 |
| `activity` | `int` | 服务端活跃度。 |
| `pre_close` | `float` | 前收/前参考值；基金及宏观指标按各自业务口径。 |
| `open` | `float` | 开盘/周期起值。 |
| `high` | `float` | 区间最高值。 |
| `low` | `float` | 区间最低值。 |
| `close` | `float` | 最新/周期结束值；宏观为报告值、基金可能为净值。 |
| `momentum` | `float` | 服务端涨跌/动量字段，未作统一百分比换算。 |
| `vol` | `int` | 服务端数量原值；不同市场和品种的数量单位需单独核对。 |
| `amount` | `float` | 服务端金额字段；EX K 线的特殊映射见对应页面。 |
| `inside_volume` | `int` | 内盘原始量。 |
| `outside_volume` | `int` | 外盘原始量。 |
| `turnover` | `float` | 服务端换手字段，保留原值。 |
| `avg` | `float` | 服务端平均价。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
