---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 板块汇总

取全部成分股报价，在本地汇总成交额、资金流及涨跌家数。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x122C / 本地聚合 | `dict[str, object]` |

## 调用签名

```text
MacClient.get_board_summary(board_symbol: str, sort_type: SortType=SortType.CHANGE_PCT, sort_order: SortOrder=SortOrder.DESC) -> dict[str, object]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `board_symbol` | `str` | 必填 | 用户看到的板块代码字符串，例如 881001；客户端先用 convert_board_code 转为请求编号。 |
| `sort_type` | `SortType` | `SortType.CHANGE_PCT` | 服务端排序字段，使用 SortType 枚举。 |
| `sort_order` | `SortOrder` | `SortOrder.DESC` | 服务端排序方向：NONE=不指定、DESC=降序、ASC=升序。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient

with MacClient() as client:
    result = client.get_board_summary("881001")
    print(result)
```

## 分页、单位与限制

这不是额外的服务端汇总命令。会分页获取成分股；成员报价缺字段时按 0 求和，结果完整性依赖字段覆盖。members 是原始 MacQuoteField 列表。up_count/down_count 用 close 与 pre_close 比较，平盘不计入两者。数量、金额沿用输入字段单位；不同板块成分可能重叠，多个板块汇总不可再直接相加。

## 返回字段

| 键 / 键组 | 含义 |
| --- | --- |
| member_count | 实际取回的成分股数。 |
| amount / vol | 按成员 fields 求和；单位沿用源字段。 |
| main_net_amount | 当日主力净额求和。 |
| main_net_3d / main_net_5d | 三日/五日主力净额求和。 |
| up_count / down_count | close 大于/小于 pre_close 的成员数。 |
| members | MacQuoteField 成员列表。 |

## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
