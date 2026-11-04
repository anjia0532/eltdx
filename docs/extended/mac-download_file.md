---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 服务器文件完整下载

查询长度后循环下载，并在内存中拼接文件。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x1215 + 0x1217 | `bytearray` |

## 调用签名

```text
MacClient.download_file(filename: str, filesize: int=0) -> bytearray
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `filename` | `str` | 必填 | 服务器支持的远端文件名/路径，不是本地磁盘路径；示例文件名只演示调用方式。 |
| `filesize` | `int` | `0` | 目标总字节数；<=0 时先查询文件元信息。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient

with MacClient() as client:
    result = client.download_file("tdxhy.cfg")
    print(result)
```

## 分页、单位与限制

filesize<=0 先查 get_file_meta；分片大小为 30000 字节，index 从 1 递增。遇空片或短片停止，当前不强制校验最终长度等于 filesize，也不做哈希校验。返回 bytearray，调用方应比较实际长度、校验内容并自行写盘。

## 返回字段

返回累计的文件字节；实际长度用 len(result) 校验。

## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
