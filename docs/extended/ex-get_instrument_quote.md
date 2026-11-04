---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# EX 单商品五档报价

查询单个扩展商品的价格、成交与五档盘口。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| ExTdxClient | 7727 | 0x23FA | `ExInstrumentQuote \| None` |

## 调用签名

```text
ExTdxClient.get_instrument_quote(market: int, code: str) -> ExInstrumentQuote | None
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | 扩展市场号 ExMarket，例如 31=港股主板、33=开放式基金、47=中金所期货、74=美股；不是标准 A 股 0/1 市场号。 |
| `code` | `str` | 必填 | 服务器证券/合约/指标代码；保留前导零，大小写遵循标的列表。A 股传六位裸代码。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import ExTdxClient

with ExTdxClient() as client:
    result = client.get_instrument_quote(47, "IFL0")
    print(result)
```

## 分页、单位与限制

本方法使用传统 EX 请求帧。仓库此前 2026-10 的默认主机实测中，元数据命令可部分使用，而本类行情命令多为超时或断开；这是历史样本，不是永久保证。支持的命令需逐台核实，TCP 连通或总数可查不代表行情可查。可对照 MAC-EX 对应能力，但它使用不同请求协议。

返回 ExInstrumentQuote 或 None，短响应会得到 None。价格字段由对应 float 直接读取；数量字段保留扩展市场原始口径，不经过 A 股手数换算。

## 返回字段

### ExInstrumentQuote

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `market` | `int` | 市场编号，按当前协议的市场表解释。 |
| `code` | `str` | 证券/合约代码字符串，保留前导零。 |
| `pre_close` | `float` | 前收/前参考值；基金及宏观指标按各自业务口径。 |
| `open` | `float` | 开盘/周期起值。 |
| `high` | `float` | 区间最高值。 |
| `low` | `float` | 区间最低值。 |
| `price` | `float` | 当前解析得到的价格；EX 成交 price 是整数原值，MAC price 是浮点值。 |
| `kaicang` | `int` | 开仓原始值。 |
| `zongliang` | `int` | 总量原始值。 |
| `xianliang` | `int` | 现量原始值。 |
| `neipan` | `int` | 内盘原始值。 |
| `waipan` | `int` | 外盘原始值。 |
| `chicang` | `int` | 持仓原始值。 |
| `bid1` | `float` | 买1档价格。 |
| `bid2` | `float` | 买2档价格。 |
| `bid3` | `float` | 买3档价格。 |
| `bid4` | `float` | 买4档价格。 |
| `bid5` | `float` | 买5档价格。 |
| `bid_vol1` | `int` | 买1档数量原值。 |
| `bid_vol2` | `int` | 买2档数量原值。 |
| `bid_vol3` | `int` | 买3档数量原值。 |
| `bid_vol4` | `int` | 买4档数量原值。 |
| `bid_vol5` | `int` | 买5档数量原值。 |
| `ask1` | `float` | 卖1档价格。 |
| `ask2` | `float` | 卖2档价格。 |
| `ask3` | `float` | 卖3档价格。 |
| `ask4` | `float` | 卖4档价格。 |
| `ask5` | `float` | 卖5档价格。 |
| `ask_vol1` | `int` | 卖1档数量原值。 |
| `ask_vol2` | `int` | 卖2档数量原值。 |
| `ask_vol3` | `int` | 卖3档数量原值。 |
| `ask_vol4` | `int` | 卖4档数量原值。 |
| `ask_vol5` | `int` | 卖5档数量原值。 |
| `_raw` | `bytes` | 本条原始记录字节，供复核；JSON 展示时需自行编码。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
