---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 服务器文件元信息

查询远端文件的偏移、大小、标志和哈希信息。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x1215 | `FileMeta` |

## 调用签名

```text
MacClient.get_file_meta(filename: str) -> FileMeta
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `filename` | `str` | 必填 | 服务器支持的远端文件名/路径，不是本地磁盘路径；示例文件名只演示调用方式。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient

with MacClient() as client:
    result = client.get_file_meta("tdxhy.cfg")
    print(result)
```

## 分页、单位与限制

filename 为服务器识别的路径，不是任意本地文件。示例文件名只示范参数，具体可用文件因服务器而异。hash 保留服务器文本，不承诺算法类型；元信息不包含文件内容。

## 返回字段

### FileMeta

| 字段 | Python 类型 | 含义与口径 |
| --- | --- | --- |
| `offset` | `int` | 文件偏移原值，单位字节。 |
| `size` | `int` | 文件大小，单位字节。 |
| `flag` | `int` | 原始标志位。 |
| `hash` | `str` | 服务器哈希文本，不承诺具体算法。 |


## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
