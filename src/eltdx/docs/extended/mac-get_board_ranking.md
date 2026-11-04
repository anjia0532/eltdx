---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 板块排行榜

按涨幅、成交额、成交量或主力净额排列板块。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x1231 + 0x122C / 本地聚合 | `list[dict[str, object]]` |

## 调用签名

```text
MacClient.get_board_ranking(board_type: BoardType=BoardType.HY, top_n: int=50, sort_by: str='change_pct', ascending: bool=False) -> list[dict[str, object]]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `board_type` | `BoardType` | `BoardType.HY` | BoardType 枚举，HY=一级行业、GN=概念、ALL=全部；完整取值见枚举页。 |
| `top_n` | `int` | `50` | 按排名截取前 N 行。 |
| `sort_by` | `str` | `'change_pct'` | 本地排序键：change_pct、amount、vol 或 main_net_amount。 |
| `ascending` | `bool` | `False` | True 升序，False 降序。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient, BoardType

with MacClient() as client:
    result = client.get_board_ranking(BoardType.HY, top_n=10, sort_by="amount")
    print(result)
```

## 分页、单位与限制

sort_by 仅接受 change_pct、amount、vol、main_net_amount。按涨幅排序时先截取再取成分汇总；其他键必须汇总全部板块后再排序，网络请求数明显增加。默认降序。缺字段按 0 的处理与板块汇总相同。

## 返回字段

| 键 / 键组 | 含义 |
| --- | --- |
| code / name | 板块代码及名称。 |
| change_pct | (price/pre_close-1)*100，四舍五入到两位；百分数而非小数比率。 |
| amount / vol / main_net_amount | 成员汇总的金额、数量、主力净额。 |
| up_count / down_count / member_count | 涨跌及总成员数。 |

## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
