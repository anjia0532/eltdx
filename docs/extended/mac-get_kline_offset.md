---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC K线索引偏移

读取 K 线索引数据的总量和返回量。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x124A | `KlineOffsetInfo` |

## 调用签名

```text
MacClient.get_kline_offset(offset: int=0, count: int=128000) -> KlineOffsetInfo
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `offset` | `int` | `0` | 协议偏移；文件接口为字节偏移，K 线索引接口为索引请求偏移。 |
| `count` | `int` | `128000` | 请求记录条数；单页还是总数及上限见本页说明，不代表服务器承诺返回足额。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient

with MacClient() as client:
    result = client.get_kline_offset(offset=0, count=128000)
    print(result)
```

## 分页、单位与限制

这是协议索引/连接验证辅助接口，不返回 K 线价格或每一条偏移记录。当前只暴露 total 和 returned；短响应映射为两个 0，不等价于已验证证券没有历史行情。

## 返回字段

### KlineOffsetInfo

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `total` | `int` | 协议报告的总量。 |
| `returned` | `int` | 当前响应的返回数量。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
