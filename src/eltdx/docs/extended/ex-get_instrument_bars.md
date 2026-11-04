---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# EX 周期K线

按周期和偏移查询扩展商品 K 线。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| ExTdxClient | 7727 | 0x23FF | `list[ExInstrumentBar]` |

## 调用签名

```text
ExTdxClient.get_instrument_bars(category: int, market: int, code: str, start: int=0, count: int=700, *, bar_time: str=BAR_TIME_START) -> list[ExInstrumentBar]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `category` | `int` | 必填 | K 线周期编号：0=5分、1=15分、2=30分、3=60分、4=日、5=周、6=月、7=1分、8=多分钟、9=多日、10=季、11=年；当前请求固定周期倍数为 1。 |
| `market` | `int` | 必填 | 扩展市场号 ExMarket，例如 31=港股主板、33=开放式基金、47=中金所期货、74=美股；不是标准 A 股 0/1 市场号。 |
| `code` | `str` | 必填 | 服务器证券/合约/指标代码；保留前导零，大小写遵循标的列表。A 股传六位裸代码。 |
| `start` | `int` | `0` | 记录起始偏移，通常从 0 开始；偏移方向与分页范围见本页说明。 |
| `count` | `int` | `700` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |
| `bar_time` | `str` | `BAR_TIME_START` | "start" 保留起点时间；"end" 对已知分钟周期移到右端点。日线不移动；范围接口另有限制。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import ExTdxClient

with ExTdxClient() as client:
    result = client.get_instrument_bars(4, 47, "IFL0", count=100)
    print(result)
```

## 分页、单位与限制

本方法使用传统 EX 请求帧。仓库此前 2026-10 的默认主机实测中，元数据命令可部分使用，而本类行情命令多为超时或断开；这是历史样本，不是永久保证。支持的命令需逐台核实，TCP 连通或总数可查不代表行情可查。可对照 MAC-EX 对应能力，但它使用不同请求协议。

参数顺序是 category, market, code；单页请求，默认 700 条，没有高层自动分页或复权。bar_time="end" 对已知分钟周期生效。amount 当前与 position 共用响应中同一 4 字节的不同类型解释，尚未建立统一成交额语义；勿直接当成交额累加。

## 返回字段

### ExInstrumentBar

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `open` | `float` | 开盘/周期起值。 |
| `high` | `float` | 区间最高值。 |
| `low` | `float` | 区间最低值。 |
| `close` | `float` | 最新/周期结束值；宏观为报告值、基金可能为净值。 |
| `position` | `int` | 持仓/位置原始字段；不同 EX K 线命令的相邻字段语义需单独核对。 |
| `trade` | `int` | 成交数量原始字段，不自动转换手数。 |
| `amount` | `float` | 普通 EX bar 对 position 的相同字节作 float 解释；范围 bar 映射 settlement，均不可直接当统一成交额。 |
| `year` | `int` | 年份。 |
| `month` | `int` | 月份。 |
| `day` | `int` | 月内日期。 |
| `hour` | `int` | 时。 |
| `minute` | `int` | 分。 |
| `_raw` | `bytes` | 本条原始记录字节，供复核；JSON 展示时需自行编码。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
