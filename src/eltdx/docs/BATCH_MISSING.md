# 批量快照与财务：缺失代码处理

本页适用于 v3.3.2 起的 `client.quotes.get_snapshots()`（7709 `0x054c`）和 `client.corporate.finance_batch()`（7709 `0x0010`）。**这些修复与 `on_missing` 参数从 v3.3.2 起提供。**升级到 v3.3.2 或更新版本后使用。#31 合入的全市场资讯方法也随 v3.3.2 发布，见 [市场资讯](methods/F10-市场资讯.md)。

## 默认严格模式

```python
from eltdx import TdxClient
from eltdx.exceptions import MissingCodesError

with TdxClient(timeout=6) as client:
    try:
        quotes = client.quotes.get_snapshots(["sh600519", "sh601198"])
    except MissingCodesError as exc:
        print("主站当前未返回：", exc.missing_codes)
```

默认 `on_missing="raise"`。确认有缺失代码时抛出 `MissingCodesError`，它继承 `ProtocolError`；`missing_codes` 是按输入顺序规范化后的完整代码元组。结果不会静默少行，也不会把 NUL 占位或正文片段包装成正常财务记录。只有整批成功，才返回正常结果。

“缺失”指本次服务器端点没有返回有效数据，不等于退市。停牌、新上市、品种不受支持及主站差异都可能影响结果；不要仅凭一次结果删除证券，也不应先按 A 股代码表过滤所有品种。

## 明确接受部分结果

```python
import warnings
from eltdx import TdxClient
from eltdx.exceptions import MissingCodesWarning

with TdxClient(timeout=6) as client:
    with warnings.catch_warnings(record=True) as notices:
        warnings.simplefilter("always", MissingCodesWarning)
        batch = client.corporate.finance_batch(
            ["sh600519", "sh601198"], on_missing="skip"
        )
    for notice in notices:
        print(notice.message)  # 列出本次跳过的完整代码
    for row in batch.records:
        print(row.full_code, row.total_shares)
```

`on_missing="skip"` 仅跳过通过单只查询确认的无数据代码，并发出 `MissingCodesWarning`（继承 `RuntimeWarning`）。全缺失且在恢复预算内时返回空集合并告警。单只请求仍返回损坏数据时抛 `ProtocolError`，即使指定 skip 也一样。

| 方法 | 返回类型 |
| --- | --- |
| `get_snapshots(codes, *, on_missing="raise")` | `list[QuoteSnapshot]` |
| `finance_batch(codes, fields=None, *, include_raw=False, on_missing="raise")` | `FinanceBatch`；设置 `fields` 时为 `list[dict]` |

跳过后保留成功代码的输入顺序，包括输入中显式重复的有效代码；字段过滤仍在本地执行。缺失代码只出现在异常或告警中，不补零、不造占位记录。可用 `row.full_code` 对齐结果，避免按原输入位置硬配。

## 恢复策略及边界

健康批次走原来的一次业务请求。只有这两种接口的特定缺失 / 记录结构异常才进入二分定位：把异常批次拆成两半，成功部分直接收集，失败部分继续拆，直到单只确认或触及预算。每次公开调用最多追加 **32 次恢复业务请求**，因此该批次至多执行 33 次；元数据查询、连接握手及底层已有重试不计入这个业务请求预算。

- 快照校验非零返回条数与请求数量，保留变长记录的原有标记边界检查；没有采用定长猜测。
- 财务校验记录长度、市场编号（0/1/2）、六位 ASCII 数字代码，以及市场和代码是否属于请求集合；拒绝额外或过量重复记录。只有整条 143 字节全零占位或空响应可作为单只无数据证据，非零坏记录继续报错。
- 单只快照的空响应，或能够完整解析但只含其他代码的响应，按“请求代码未返回”处理；后者绝不将其他代码的行情交付给调用者。单只缺失标记且数据损坏时仍报错。
- 连接错误、超时和不相关协议错误直接传播，不二分，也不因 skip 隐藏。
- 恢复预算耗尽抛 `ProtocolError`，不交付已经收集的部分结果；大量无数据代码建议缩小调用批次。
- 单次正常财务结果中 `include_raw=True` 保留服务端 payload；经过拆分重组的结果没有唯一对应的原始报文，`raw_payload=b""`。单条记录原始字段按原实现保留。

原始协议解析函数不执行二分恢复；策略位于上述两个 Python 业务 API。MCP 现有快照 / 财务工具使用默认严格模式，未增加 skip 参数；HTTP / WebSocket 通用 RPC 可在这两个业务方法的 `params` 中传 `on_missing`。

## 排错

`MissingCodesError` 表示定位到了无数据代码；`ProtocolError` 中的 invalid record / unexpected or duplicate record 表示记录校验失败；budget exhausted 表示恢复请求用尽。财务异常包含记录索引、条数、payload 长度，坏记录还包含截断的十六进制头，方便定位，避免整段响应输出。

这类业务数据异常与请求响应串包不是同一结论。本次复核的异常原始 TCP 响应中消息 ID 与命令均匹配；运行时原有消息 ID、命令类型和连接代次校验继续保留。
