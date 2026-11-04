---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 成交明细

查询当日或指定日期的带秒成交明细；支持自动分页。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x122F | `list[MacTransaction]` |

## 调用签名

```text
MacClient.get_transactions(market: int, code: str, count: int=2000, start: int=0, date: int | None=None) -> list[MacTransaction]
MacClient.get_stock_transaction(market: int, code: str, count: int=2000, start: int=0, date: int | None=None) -> list[MacTransaction]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | MAC 市场编号；A 股常用 0=深、1=沪。板块等品种请沿用枚举/列表返回的市场号，不与 ExMarket 混用。 |
| `code` | `str` | 必填 | 服务器证券/合约/指标代码；保留前导零，大小写遵循标的列表。A 股传六位裸代码。 |
| `count` | `int` | `2000` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |
| `start` | `int` | `0` | 记录起始偏移，通常从 0 开始；偏移方向与分页范围见本页说明。 |
| `date` | `int \| None` | `None` | YYYYMMDD 整数；默认 None 时请求最新/当前交易日数据。按服务器实际留存范围返回。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient

with MacClient() as client:
    result = client.get_transactions(1, "600519", date=20261029, count=100)
    print(result)
```

## 分页、单位与限制

get_stock_transaction 是完全相同的别名。count 为总请求数，按最多 1000 条/页发出。start=0 取最新一段，偏移增大向更早查询；2026-10-30 实测单页时间升序，但高层多页直接追加，所以最终列表未必全局升序。历史日查询可在本地 sorted(rows, key=lambda row: row.time)；盘中翻页期间新增记录可能改变偏移，单靠排序不解决重复/遗漏。

时间字段是真实响应的 uint32 当日秒数。实测约 3 秒一条且 trade_count 可大于 1，是聚合成交明细，不等于 Level-2 每笔撮合。不同主机同一收盘记录曾相差 1 秒，不宜据此判断微观事件先后。价格是 float32，会有小数误差；vol 保留服务端原始单位，跨品种使用前先核对每手/数量口径。

响应头带交易日期，但当前 MacTransaction 只返回 time，不保留响应日期；None 查询在非交易日可能得到最近交易日数据，业务上应自行核实日期。历史保留深度随服务器变化，本次测到 2026-09-30，不代表最早界限。

## 返回字段

### MacTransaction

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `time` | `time` | 当日时间，无日期与时区；MacSymbolInfo 为完整 datetime。 |
| `price` | `float` | 当前解析得到的价格；EX 成交 price 是整数原值，MAC price 是浮点值。 |
| `vol` | `int` | 服务端数量原值；不同市场和品种的数量单位需单独核对。 |
| `trade_count` | `int` | 服务端成交笔数；聚合记录可 >1，港股 EX 转换模型固定为 0（未提供）。 |
| `bs_flag` | `int` | 原始买卖/状态值；MAC 常见 0=买、1=卖、2=中性、5=盘后；跨市场需核对。 |


## 真实响应节选（2026-10-30）

对深市 000001 的本次实测。下列数据来自服务器响应，不是构造测试；价格保留 float32 解码结果。

```json
[
  {
    "time_seconds_raw": 49869,
    "time": "13:51:09",
    "price": 11.640000343322754,
    "vol": 1091,
    "trade_count": 17,
    "bs_flag": 1
  },
  {
    "time_seconds_raw": 49872,
    "time": "13:51:12",
    "price": 11.649999618530273,
    "vol": 282,
    "trade_count": 28,
    "bs_flag": 0
  },
  {
    "time_seconds_raw": 49875,
    "time": "13:51:15",
    "price": 11.649999618530273,
    "vol": 1132,
    "trade_count": 45,
    "bs_flag": 0
  }
]
```

原始秒数直接位于每条 18 字节记录的前 4 字节。解压后响应体的记录起点是 39，布局 `<IfIIH`，分别为秒数、价格、量、笔数、状态；响应体偏移 24 的 uint32 是 YYYYMMDD 日期，偏移 29 为 uint16 条数。当前高层丢弃头部日期，查询历史时应保留请求日期。

### 与其他成交入口的区别

| 入口 | 协议 | 时间与语义 |
| --- | --- | --- |
| TdxClient.trades.today/history | 0x0FC5 / 0x0FC6 | 标准 A 股成交明细，分钟字段。 |
| MacClient.get_transactions | 0x122F | MAC A 股明细，真实秒字段，可含多笔聚合。 |
| MacExClient.goods_transaction | 按市场路由 | 港股股票类走 EX，其他扩展市场走 MAC。 |

## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
