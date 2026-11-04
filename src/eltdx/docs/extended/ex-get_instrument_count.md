---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# EX 商品总数

读取全市场商品总数。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| ExTdxClient | 7727 | 0x23F0 | `int` |

## 调用签名

```text
ExTdxClient.get_instrument_count() -> int
```

## 参数

无业务参数。

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.ex import ExTdxClient

with ExTdxClient() as client:
    result = client.get_instrument_count()
    print(result)
```

## 分页、单位与限制

无 market 参数；返回 int。短于解析要求的响应当前返回 0；应区分正常零与异常短响应。总数可变，遍历时保留市场号及代码，不把全局偏移当永久 ID。

## 返回字段

返回单个整数；其计数范围见上面的说明。

## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/ex/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
