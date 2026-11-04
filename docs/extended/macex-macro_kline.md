---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC-EX 宏观指标历史序列

借用 K 线模型读取宏观指标的历史报告期序列。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacExClient | 7727 | 0x122E / 市场38 | `list[MacBar]` |

## 调用签名

```text
MacExClient.macro_kline(code: str, period: Period=Period.MONTHLY, start: int=0, count: int=800, adjust: Adjust=Adjust.NONE) -> list[MacBar]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `code` | `str` | 必填 | 完整宏观代码如 1_GDP，或唯一裸代码如 GDP；重名抛 ValueError，未知裸代码抛 ProtocolError。 |
| `period` | `Period` | `Period.MONTHLY` | Period 枚举；常用 DAILY、MIN_1、MIN_5、MONTHLY 等。枚举存在不代表全部服务器都有对应数据。 |
| `start` | `int` | `0` | 记录起始偏移，通常从 0 开始；偏移方向与分页范围见本页说明。 |
| `count` | `int` | `800` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |
| `adjust` | `Adjust` | `Adjust.NONE` | Adjust.NONE=不复权、QFQ=前复权、HFQ=后复权；服务端是否支持取决于品种。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import MacExClient
from eltdx.mac import Period

with MacExClient() as client:
    result = client.macro_kline("1_GDP", period=Period.YEARLY, count=40)
    print(result)
```

## 分页、单位与限制

默认 MONTHLY；GDP 可选 YEARLY/QUARTERLY，CPI/PMI/M2 通常 MONTHLY，日利率用 DAILY，需按指标实际服务周期核对。MacBar.close 才是当期值，日期是服务器报告期标签，不是发布时点，更不是已知可交易信息时间。数量/金额通常为 0。单次请求，无自动取全或修订版本历史；建议 adjust=NONE，指标不适用股票复权。

## 返回字段

### MacBar

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `datetime` | `datetime` | 服务器日期时间，无时区；时间起止口径见调用参数。 |
| `open` | `float` | 开盘/周期起值。 |
| `high` | `float` | 区间最高值。 |
| `low` | `float` | 区间最低值。 |
| `close` | `float` | 最新/周期结束值；宏观为报告值、基金可能为净值。 |
| `vol` | `float` | 服务端数量原值；不同市场和品种的数量单位需单独核对。 |
| `amount` | `float` | 服务端金额字段；EX K 线的特殊映射见对应页面。 |
| `float_shares` | `float` | 协议流通量字段，保持原值，未统一股/万股口径。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/mac_client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
