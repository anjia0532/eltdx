---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 板块多日涨幅排行

从板块日线计算窗口涨幅后在本地排序。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x1231 + 0x122E / 本地计算 | `list[dict[str, object]]` |

## 调用签名

```text
MacClient.get_board_change_ranking(board_type: BoardType=BoardType.HY, target_date: int | None=None, days: int=20, top_n: int | None=None, ascending: bool=False) -> list[dict[str, object]]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `board_type` | `BoardType` | `BoardType.HY` | BoardType 枚举，HY=一级行业、GN=概念、ALL=全部；完整取值见枚举页。 |
| `target_date` | `int \| None` | `None` | YYYYMMDD 整数或 None；选不晚于该日期的记录，None 使用取回数据中的最新日期。 |
| `days` | `int` | `20` | 涨幅计算的交易日窗口，要求 >=1；实际数据不足时的行为见本页。 |
| `top_n` | `int \| None` | `None` | 按排名截取前 N 行；None 不截断。 |
| `ascending` | `bool` | `False` | True 升序，False 降序。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient, BoardType

with MacClient() as client:
    result = client.get_board_change_ranking(BoardType.HY, days=20, top_n=10)
    print(result)
```

## 分页、单位与限制

每个板块只取最新 days+10 根不复权日线，再选 <=target_date 的终点；target_date 很早时并不会继续回溯历史，可能整块被跳过。窗口起点为 max(0,end_pos-days)，数据不足会用更短区间；不能直接当作全样本严格 N 日回报。少于两根、零起点价、传输失败的板块会跳过。

## 返回字段

| 键 / 键组 | 含义 |
| --- | --- |
| code / name | 板块代码及名称。 |
| close_end / close_start | 实际选取的终点、起点收盘价。 |
| change_pct | (close_end/close_start-1)*100，四舍五入到两位。 |

## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
