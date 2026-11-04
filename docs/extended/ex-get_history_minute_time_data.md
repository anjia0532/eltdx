---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# EX 历史分时

读取指定日期的扩展商品分时点。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| ExTdxClient | 7727 | 0x240C | `list[ExMinuteBar]` |

## 调用签名

```text
ExTdxClient.get_history_minute_time_data(market: int, code: str, date: int) -> list[ExMinuteBar]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | 扩展市场号 ExMarket，例如 31=港股主板、33=开放式基金、47=中金所期货、74=美股；不是标准 A 股 0/1 市场号。 |
| `code` | `str` | 必填 | 服务器证券/合约/指标代码；保留前导零，大小写遵循标的列表。A 股传六位裸代码。 |
| `date` | `int` | 必填 | YYYYMMDD 整数；默认 None 时请求最新/当前交易日数据。按服务器实际留存范围返回。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import ExTdxClient

with ExTdxClient() as client:
    result = client.get_history_minute_time_data(47, "IFL0", date=20261029)
    print(result)
```

## 分页、单位与限制

本方法使用传统 EX 请求帧。仓库此前 2026-10 的默认主机实测中，元数据命令可部分使用，而本类行情命令多为超时或断开；这是历史样本，不是永久保证。支持的命令需逐台核实，TCP 连通或总数可查不代表行情可查。可对照 MAC-EX 对应能力，但它使用不同请求协议。

date 为 YYYYMMDD 整数；返回字段与当日分时相同，不含日期，调用方保存请求日期。无多日自动循环，历史深度取决于主机。

## 返回字段

### ExMinuteBar

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `hour` | `int` | 时。 |
| `minute` | `int` | 分。 |
| `price` | `float` | 当前解析得到的价格；EX 成交 price 是整数原值，MAC price 是浮点值。 |
| `avg_price` | `float` | 服务端分时平均价。 |
| `volume` | `int` | 成交/分时数量原值，未统一股数或手数。 |
| `open_interest` | `int` | EX 分时最后一个 uint32 的映射名，业务语义按市场核对。 |
| `_raw` | `bytes` | 本条原始记录字节，供复核；JSON 展示时需自行编码。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
