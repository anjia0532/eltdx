---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC-EX 单日分时

读取扩展市场某日分时曲线。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacExClient | 7727 | 0x122D | `MacTickChart` |

## 调用签名

```text
MacExClient.goods_tick_chart(market: int, code: str, query_date: date | None=None) -> MacTickChart
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | 扩展市场号 ExMarket，例如 31=港股主板、33=开放式基金、47=中金所期货、74=美股；不是标准 A 股 0/1 市场号。 |
| `code` | `str` | 必填 | 服务器证券/合约/指标代码；保留前导零，大小写遵循标的列表。A 股传六位裸代码。 |
| `query_date` | `date \| None` | `None` | datetime.date 对象或 None；不同于 MacClient 的整数 date 参数。None 表示当前数据。 |

## 使用示例

示例代码用于展示调用方式。

```python
from datetime import date
from eltdx.ex import MacExClient

with MacExClient() as client:
    result = client.goods_tick_chart(74, "AAPL", query_date=date(2026, 10, 29))
    print(result)
```

## 分页、单位与限制

query_date 为 datetime.date，不接受 MacClient 示例中的 YYYYMMDD 整数。单次请求，无多日分时封装。时间按服务器原值解析，不带时区，也不自动在市场时区与北京时间之间转换；跨时区比较先核实服务器时间口径与日期。

## 返回字段

### MacTickChart

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `market` | `int` | 市场编号，按当前协议的市场表解释。 |
| `code` | `str` | 证券/合约代码字符串，保留前导零。 |
| `name` | `str` | 名称文本；GoodsItem 的特殊语义见该模型。 |
| `pre_close` | `float` | 前收/前参考值；基金及宏观指标按各自业务口径。 |
| `open` | `float` | 开盘/周期起值。 |
| `high` | `float` | 区间最高值。 |
| `low` | `float` | 区间最低值。 |
| `close` | `float` | 最新/周期结束值；宏观为报告值、基金可能为净值。 |
| `vol` | `int` | 服务端数量原值；不同市场和品种的数量单位需单独核对。 |
| `amount` | `float` | 服务端金额字段；EX K 线的特殊映射见对应页面。 |
| `turnover` | `float` | 服务端换手字段，保留原值。 |
| `avg` | `float` | 服务端平均价。 |
| `charts` | `list[MacTick]` | 曲线列表；单日为 MacTick，多日为 MacMultiTickDay。 |

### MacTick

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `time` | `time` | 当日时间，无日期与时区；MacSymbolInfo 为完整 datetime。 |
| `price` | `float` | 当前解析得到的价格；EX 成交 price 是整数原值，MAC price 是浮点值。 |
| `avg` | `float` | 服务端平均价。 |
| `vol` | `int` | 服务端数量原值；不同市场和品种的数量单位需单独核对。 |
| `momentum` | `float` | 服务端涨跌/动量字段，未作统一百分比换算。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/mac_client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
