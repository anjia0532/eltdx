---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 多日分时

一次获取最多五个交易日的分时曲线。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x123E | `MacMultiTickChart` |

## 调用签名

```text
MacClient.get_tick_charts(market: int, code: str, date: int | None=None, days: int=5) -> MacMultiTickChart
MacClient.get_stock_minute_time_hist(market: int, code: str, date: int | None=None, days: int=5) -> MacMultiTickChart
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | MAC 市场编号；A 股常用 0=深、1=沪。板块等品种请沿用枚举/列表返回的市场号，不与 ExMarket 混用。 |
| `code` | `str` | 必填 | 服务器证券/合约/指标代码；保留前导零，大小写遵循标的列表。A 股传六位裸代码。 |
| `date` | `int \| None` | `None` | YYYYMMDD 整数；默认 None 时请求最新/当前交易日数据。按服务器实际留存范围返回。 |
| `days` | `int` | `5` | 交易日数量，协议范围 1..5。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient

with MacClient() as client:
    result = client.get_tick_charts(0, "000001", days=5)
    print(result)
```

## 分页、单位与限制

get_stock_minute_time_hist 是完全相同的别名。days 的协议范围为 1..5；构造命令会校验。date=None 从最新交易日开始，交易日不是自然日。外层 charts 按日分组，每日 date / pre_close / ticks 分别保存日期、昨收及采样点。

## 返回字段

### MacMultiTickChart

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
| `charts` | `list[MacMultiTickDay]` | 曲线列表；单日为 MacTick，多日为 MacMultiTickDay。 |

### MacMultiTickDay

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `date` | `date` | 交易日期；CapitalFlowData 当前固定为空字符串。 |
| `pre_close` | `float` | 前收/前参考值；基金及宏观指标按各自业务口径。 |
| `ticks` | `list[MacTick]` | 该日的 MacTick 采样点列表。 |

### MacTick

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `time` | `time` | 当日时间，无日期与时区；MacSymbolInfo 为完整 datetime。 |
| `price` | `float` | 当前解析得到的价格；EX 成交 price 是整数原值，MAC price 是浮点值。 |
| `avg` | `float` | 服务端平均价。 |
| `vol` | `int` | 服务端数量原值；不同市场和品种的数量单位需单独核对。 |
| `momentum` | `float` | 服务端涨跌/动量字段，未作统一百分比换算。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
