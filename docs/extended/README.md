---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# EX / MAC / MAC-EX 接口单页索引

这里覆盖当前三个同步客户端的全部公开业务方法。连接、探活、关闭与健康状态按客户端集中说明；语义别名共用同一页。方法有实现不代表任意默认服务器都服务该命令，线上覆盖见[通道概览](../EXTENDED_MARKET.md)。

- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)

## MAC（7709）

[连接、探活与错误处理](mac-连接与主机.md)

| 方法 | 协议 / 实现 | 返回 | 单页文档 |
| --- | --- | --- | --- |
| `MacClient.get_stock_quotes` | 0x122B | list[MacQuoteField] | [批量报价](mac-get_stock_quotes.md) |
| `MacClient.get_stock_quotes_list` | 0x122C | list[MacQuoteField] | [分类排行](mac-get_stock_quotes_list.md) |
| `MacClient.get_stock_kline` | 0x122E | list[MacBar] | [复权K线](mac-get_stock_kline.md) |
| `MacClient.get_tick_chart`（别名 `get_stock_minute_time`） | 0x122D | MacTickChart | [单日分时](mac-get_tick_chart.md) |
| `MacClient.get_tick_charts`（别名 `get_stock_minute_time_hist`） | 0x123E | MacMultiTickChart | [多日分时](mac-get_tick_charts.md) |
| `MacClient.get_chart_sampling` | 0x254D | list[float] | [分时缩略采样](mac-get_chart_sampling.md) |
| `MacClient.get_transactions`（别名 `get_stock_transaction`） | 0x122F | list[MacTransaction] | [成交明细](mac-get_transactions.md) |
| `MacClient.get_symbol_info` | 0x122A | MacSymbolInfo | [个股特征快照](mac-get_symbol_info.md) |
| `MacClient.get_board_list` | 0x1231 | list[BoardInfo] | [板块列表](mac-get_board_list.md) |
| `MacClient.get_board_members` | 0x122C | list[MacQuoteField] | [板块成分股报价](mac-get_board_members.md) |
| `MacClient.get_belong_board` | 0x1218 / head_flag=1 | list[BelongBoardInfo] | [个股所属板块](mac-get_belong_board.md) |
| `MacClient.get_board_summary` | 0x122C / 本地聚合 | dict[str, object] | [板块汇总](mac-get_board_summary.md) |
| `MacClient.get_board_ranking` | 0x1231 + 0x122C / 本地聚合 | list[dict[str, object]] | [板块排行榜](mac-get_board_ranking.md) |
| `MacClient.get_board_change_ranking` | 0x1231 + 0x122E / 本地计算 | list[dict[str, object]] | [板块多日涨幅排行](mac-get_board_change_ranking.md) |
| `MacClient.get_capital_flow` | 0x1218 / head_flag=2 | CapitalFlowData \| None | [个股资金流](mac-get_capital_flow.md) |
| `MacClient.get_auction` | 0x123D | list[AuctionItem] | [集合竞价](mac-get_auction.md) |
| `MacClient.get_unusual` | 0x1237 | list[UnusualItem] | [市场盘口异动](mac-get_unusual.md) |
| `MacClient.get_server_info` | 0x120F | ServerSession | [服务器交易时段](mac-get_server_info.md) |
| `MacClient.get_kline_offset` | 0x124A | KlineOffsetInfo | [K线索引偏移](mac-get_kline_offset.md) |
| `MacClient.get_file_meta` | 0x1215 | FileMeta | [服务器文件元信息](mac-get_file_meta.md) |
| `MacClient.download_file_chunk` | 0x1217 | bytes | [服务器文件分片](mac-download_file_chunk.md) |
| `MacClient.download_file` | 0x1215 + 0x1217 | bytearray | [服务器文件完整下载](mac-download_file.md) |
| `MacClient.get_goods_list` | 0x2562 | list[GoodsItem] | [商品列表](mac-get_goods_list.md) |

## EX（7727）

[连接、探活与错误处理](ex-连接与主机.md)

| 方法 | 协议 / 实现 | 返回 | 单页文档 |
| --- | --- | --- | --- |
| `ExTdxClient.get_markets` | 0x23F4 | list[ExMarketInfo] | [市场列表](ex-get_markets.md) |
| `ExTdxClient.get_instrument_count` | 0x23F0 | int | [商品总数](ex-get_instrument_count.md) |
| `ExTdxClient.get_instrument_info` | 0x23F5 | list[ExInstrumentInfo] | [商品信息](ex-get_instrument_info.md) |
| `ExTdxClient.get_instrument_quote` | 0x23FA | ExInstrumentQuote \| None | [单商品五档报价](ex-get_instrument_quote.md) |
| `ExTdxClient.get_instrument_quote_list` | 0x2400 | list[OrderedDict[str, object]] | [分类报价列表](ex-get_instrument_quote_list.md) |
| `ExTdxClient.get_instrument_bars` | 0x23FF | list[ExInstrumentBar] | [周期K线](ex-get_instrument_bars.md) |
| `ExTdxClient.get_history_instrument_bars_range` | 0x240D | list[ExInstrumentBar] | [日期范围历史K线](ex-get_history_instrument_bars_range.md) |
| `ExTdxClient.get_minute_time_data` | 0x240B | list[ExMinuteBar] | [当日分时](ex-get_minute_time_data.md) |
| `ExTdxClient.get_history_minute_time_data` | 0x240C | list[ExMinuteBar] | [历史分时](ex-get_history_minute_time_data.md) |
| `ExTdxClient.get_transaction_data` | 0x23FC | list[ExTransactionRecord] | [当日成交明细](ex-get_transaction_data.md) |
| `ExTdxClient.get_history_transaction_data` | 0x2406 | list[ExTransactionRecord] | [历史成交明细](ex-get_history_transaction_data.md) |

## MAC-EX（7727）

[连接、探活与错误处理](macex-连接与主机.md)

| 方法 | 协议 / 实现 | 返回 | 单页文档 |
| --- | --- | --- | --- |
| `MacExClient.instruments` | 0x23F0 + 0x23F5 | list[ExInstrumentInfo] | [标的元数据](macex-instruments.md) |
| `MacExClient.goods_count` | 0x23F0 / 0x2562 / 0x23F5 | int | [商品数量](macex-goods_count.md) |
| `MacExClient.goods_list` | 0x2562 / 0x23F5 | list[GoodsItem] | [商品列表](macex-goods_list.md) |
| `MacExClient.goods_quotes` | 0x122B | list[MacQuoteField] | [批量报价与净值](macex-goods_quotes.md) |
| `MacExClient.goods_quotes_list` | 0x2562 / 0x23F5 + 0x122B | list[MacQuoteField] | [列表报价](macex-goods_quotes_list.md) |
| `MacExClient.goods_kline` | 0x122E | list[MacBar] | [扩展市场K线](macex-goods_kline.md) |
| `MacExClient.goods_tick_chart` | 0x122D | MacTickChart | [单日分时](macex-goods_tick_chart.md) |
| `MacExClient.goods_chart_sampling` | 0x254D | list[float] | [分时缩略采样](macex-goods_chart_sampling.md) |
| `MacExClient.goods_transaction` | 0x122F / 0x23FC / 0x2406 | list[MacTransaction] | [成交明细](macex-goods_transaction.md) |
| `MacExClient.goods_transaction_all` | 0x23FC / 0x2406 | list[MacTransaction] | [港股全量成交](macex-goods_transaction_all.md) |
| `MacExClient.macro_indicators` | 0x2562 / 市场38 | list[GoodsItem] | [宏观指标列表](macex-macro_indicators.md) |
| `MacExClient.macro_quotes` | 0x122B / 市场38 | list[MacQuoteField] | [宏观指标最新值](macex-macro_quotes.md) |
| `MacExClient.macro_kline` | 0x122E / 市场38 | list[MacBar] | [宏观指标历史序列](macex-macro_kline.md) |

## 宏观类别常量

MacExClient.MACRO_CATEGORIES 是类别前缀到中文名的映射，代码前缀并不代表服务器已返回对应序列。

| 前缀 | 类别 |
| --- | --- |
| 1 | 国民经济 |
| 2 | 物价 |
| 3 | 景气指数 |
| 4 | 对外经济 |
| 5 | 货币金融 |
| 6 | 房地产与其他 |
| 7 | 证券市场 |
| 8 | 美国经济 |
| 9 | 利率与回购 |

## 读文档时的约定

- “示例”只演示调用；真实响应会标日期与采样范围，不把构造测试写成线上数据。
- count 可能为单页上限或总数，以各页为准；空/短页、返回条数及全量安全上限分别说明。
- 未确认的量/金额/价格口径保留协议值；跨市场分析前核对元数据，不自动套 A 股单位。
- MAC 0x122F 有秒，不代表 Level-2 逐笔；标准 0x0FC5/0x0FC6 为分钟字段。
