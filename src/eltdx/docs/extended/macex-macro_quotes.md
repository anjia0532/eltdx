---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC-EX 宏观指标最新值

读取宏观指标最新报告值及前值等字段。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacExClient | 7727 | 0x122B / 市场38 | `list[MacQuoteField]` |

## 调用签名

```text
MacExClient.macro_quotes(codes: 'str | Iterable[str]', fields: Any=None) -> list[MacQuoteField]
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `codes` | `'str \| Iterable[str]'` | 必填 | 单个宏观代码字符串或代码序列；如 1_GDP、GDP；完整前缀优先。 |
| `fields` | `Any` | `None` | FieldBit、PresetField 或 FieldSelection 字段集合；仅请求的字段进入 fields 字典，默认集合见说明。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import MacExClient

with MacExClient() as client:
    result = client.macro_quotes(["1_GDP"])
    print(result)
```

## 分页、单位与限制

完整代码含下划线时直接使用，不再次校验是否存在。裸代码按缓存 name 后缀匹配：唯一匹配补类别，多匹配抛 ValueError 列出候选，未匹配抛 ProtocolError。空列表不发请求。推荐先枚举指标再选择真实代码。close 表示指标值，不是证券价格，更新频率及单位由指标定义；pre_close 通常是前报告期，不能保证是昨日值。vol/amount 为 0 不表示宏观量为零。

## 返回字段

### MacQuoteField

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `market` | `int` | 市场编号，按当前协议的市场表解释。 |
| `code` | `str` | 证券/合约代码字符串，保留前导零。 |
| `name` | `str` | 名称文本；GoodsItem 的特殊语义见该模型。 |
| `fields` | `dict[str, Any]` | 按请求位图解析的动态字典；键名为 FieldBit.field_name。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/mac_client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
