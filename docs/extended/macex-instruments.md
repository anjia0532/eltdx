---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC-EX 标的元数据

读取某个扩展市场内的代码、名称、类别及描述。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacExClient | 7727 | 0x23F0 + 0x23F5 | `list[ExInstrumentInfo]` |

## 调用签名

```text
MacExClient.instruments(market: int, start: int=0, count: int=600) -> list[ExInstrumentInfo]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `market` | `int` | 必填 | 扩展市场号 ExMarket，例如 31=港股主板、33=开放式基金、47=中金所期货、74=美股；不是标准 A 股 0/1 市场号。 |
| `start` | `int` | `0` | 记录起始偏移，通常从 0 开始；偏移方向与分页范围见本页说明。 |
| `count` | `int` | `600` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import MacExClient

with MacExClient() as client:
    result = client.instruments(33, start=0, count=10)
    print(result)
```

## 分页、单位与限制

start 是市场内偏移。根据全表 market 有序的前提二分定位边界，实例缓存市场区间，再分页筛选；count<=0 返回空。服务器列表变化时已有区间缓存可能过时，可新建客户端重新查询。相比 goods_list，此方法返回真正的 code 和 name，适合基金/外盘枚举。

## 返回字段

### ExInstrumentInfo

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `category` | `int` | 商品/市场类别原始编号，与 K 线周期 category 并非同一概念。 |
| `market` | `int` | 市场编号，按当前协议的市场表解释。 |
| `code` | `str` | 证券/合约代码字符串，保留前导零。 |
| `name` | `str` | 名称文本；GoodsItem 的特殊语义见该模型。 |
| `desc` | `str` | 描述文本。 |
| `_raw` | `bytes` | 本条原始记录字节，供复核；JSON 展示时需自行编码。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/mac_client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
