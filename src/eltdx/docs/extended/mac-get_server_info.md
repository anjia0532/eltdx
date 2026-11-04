---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 服务器交易时段

读取服务器日期、最近交易日和两组交易时段参数。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x120F | `ServerSession` |

## 调用签名

```text
MacClient.get_server_info() -> ServerSession
```

## 参数

无业务参数。

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient

with MacClient() as client:
    result = client.get_server_info()
    print(result)
```

## 分页、单位与限制

单次服务器状态查询，不是某个证券的交易日历。market_param_1/2 保留原始值，未赋予统一业务含义；today 与 last_trading_day 应区别使用。

## 返回字段

### ServerSession

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `today` | `str` | 服务器当日日期文本。 |
| `last_trading_day` | `str` | 服务器最近交易日文本。 |
| `sessions_1` | `list[dict[str, Any]]` | 第一组四个交易时段字典，每项只含 open、close，时间格式为 H:MM。 |
| `sessions_2` | `list[dict[str, Any]]` | 第二组四个交易时段字典，每项只含 open、close，时间格式为 H:MM。 |
| `market_param_1` | `int` | 原始市场参数 1，尚未赋予统一业务语义。 |
| `market_param_2` | `int` | 原始市场参数 2，尚未赋予统一业务语义。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
