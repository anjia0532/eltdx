---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# EX 市场列表

查询服务器提供的市场描述表。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| ExTdxClient | 7727 | 0x23F4 | `list[ExMarketInfo]` |

## 调用签名

```text
ExTdxClient.get_markets() -> list[ExMarketInfo]
```

## 参数

无业务参数。

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import ExTdxClient

with ExTdxClient() as client:
    result = client.get_markets()
    print(result)
```

## 分页、单位与限制

仓库此前默认主机实测均超时，Python 方法本身没有枚举回退。只需要已知市场号时可离线使用 eltdx.ex.ExMarket；CLI 回退逻辑不代表此 Python 方法也回退。

## 返回字段

### ExMarketInfo

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `market` | `int` | 市场编号，按当前协议的市场表解释。 |
| `category` | `int` | 商品/市场类别原始编号，与 K 线周期 category 并非同一概念。 |
| `name` | `str` | 名称文本；GoodsItem 的特殊语义见该模型。 |
| `short_name` | `str` | 市场简称。 |
| `_raw` | `bytes` | 本条原始记录字节，供复核；JSON 展示时需自行编码。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
