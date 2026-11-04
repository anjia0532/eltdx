---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC-EX 宏观指标列表

枚举并缓存市场 38 的宏观指标代码。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacExClient | 7727 | 0x2562 / 市场38 | `list[GoodsItem]` |

## 调用签名

```text
MacExClient.macro_indicators() -> list[GoodsItem]
```

## 参数

无业务参数。

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import MacExClient

with MacExClient() as client:
    result = client.macro_indicators()
    print(result)
```

## 分页、单位与限制

当前调用 goods_list(38,0,600)，最多请求 600 项，首次结果建立实例缓存，后续重复调用直接返回缓存；此前实测 217 个、9 类是样本数量，不是固定协议常量。GoodsItem.name 用作 1_GDP 这类代码键，并非保证中文名称。空缓存后续会重试。需完整代码/中文名称时结合实际 instruments / quotes 响应核对。

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
