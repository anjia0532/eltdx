---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC-EX 商品列表

读取市场商品列表，MAC 列表为空时回退 EX 元数据。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacExClient | 7727 | 0x2562 / 0x23F5 | `list[GoodsItem]` |

## 调用签名

```text
MacExClient.goods_list(market: int, start: int=0, count: int=600) -> list[GoodsItem]
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
    result = client.goods_list(33, start=0, count=20)
    print(result)
```

## 分页、单位与限制

高层以 600 条分页，截到 count；不支持服务端排序。若首轮已有部分 MAC 数据，不会用回退补足尾部。name 在原协议及回退模型里存代码；code 是浮点占位列表。需要中文名称使用 instruments；不要把 GoodsItem.name 标成一定是中文指标名称。

## 返回字段

### GoodsItem

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `name` | `str` | 本协议通常存代码，如 1_GDP / IFL0；不是保证的中文名称。 |
| `category` | `int` | 商品/市场类别原始编号，与 K 线周期 category 并非同一概念。 |
| `u` | `int` | 保留的原始协议字段 u，未建立稳定业务语义。 |
| `index` | `int` | 协议序号/索引；商品索引不是永久证券 ID。 |
| `switch` | `int` | 保留的原始协议开关值。 |
| `code` | `list[float]` | 三个浮点协议槽位，非证券代码字符串；回退路径也可能填浮点占位。 |
| `c1` | `int` | 保留的原始协议字段 c1。 |
| `c2` | `int` | 保留的原始协议字段 c2。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/mac_client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
