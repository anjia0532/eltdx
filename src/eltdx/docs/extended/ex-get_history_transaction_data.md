---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# EX 历史成交明细

单页读取指定日期的扩展商品成交明细。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| ExTdxClient | 7727 | 0x2406 | `list[ExTransactionRecord]` |

## 调用签名

```text
ExTdxClient.get_history_transaction_data(market: int, code: str, date: int, start: int=0, count: int=1800) -> list[ExTransactionRecord]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | 扩展市场号 ExMarket，例如 31=港股主板、33=开放式基金、47=中金所期货、74=美股；不是标准 A 股 0/1 市场号。 |
| `code` | `str` | 必填 | 服务器证券/合约/指标代码；保留前导零，大小写遵循标的列表。A 股传六位裸代码。 |
| `date` | `int` | 必填 | YYYYMMDD 整数；默认 None 时请求最新/当前交易日数据。按服务器实际留存范围返回。 |
| `start` | `int` | `0` | 记录起始偏移，通常从 0 开始；偏移方向与分页范围见本页说明。 |
| `count` | `int` | `1800` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import ExTdxClient

with ExTdxClient() as client:
    result = client.get_history_transaction_data(31, "00700", date=20261029, start=0, count=100)
    print(result)
```

## 分页、单位与限制

本方法使用传统 EX 请求帧。仓库此前 2026-10 的默认主机实测中，元数据命令可部分使用，而本类行情命令多为超时或断开；这是历史样本，不是永久保证。支持的命令需逐台核实，TCP 连通或总数可查不代表行情可查。可对照 MAC-EX 对应能力，但它使用不同请求协议。

date 为 YYYYMMDD 整数，start/count 分页需要调用方管理；该方法没有港股全量自动翻页。价格整数、秒有效性处理与当日 EX 成交相同。需要港股自动翻页及港元价格时使用 MacExClient.goods_transaction / goods_transaction_all。

## 返回字段

### ExTransactionRecord

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `hour` | `int` | 时。 |
| `minute` | `int` | 分。 |
| `second` | `int` | 秒；传统 EX 解析遇非法秒会置 0。 |
| `price` | `int` | 整数原始价；港股统一封装另做 /1000，直接 EX 调用不换算。 |
| `volume` | `int` | 成交/分时数量原值，未统一股数或手数。 |
| `zengcang` | `int` | 增仓原始带符号整数。 |
| `nature` | `int` | direction//10000 得到的方向/性质编号。 |
| `_raw` | `bytes` | 本条原始记录字节，供复核；JSON 展示时需自行编码。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
