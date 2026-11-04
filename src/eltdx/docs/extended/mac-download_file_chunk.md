---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 服务器文件分片

下载远端文件的一段原始字节。

| 客户端 | 端口 | 协议 / 实现 | 返回类型 |
| --- | --- | --- | --- |
| MacClient | 7709 | 0x1217 | `bytes` |

## 调用签名

```text
MacClient.download_file_chunk(filename: str, index: int, offset: int, size: int) -> bytes
```

## 参数

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `filename` | `str` | 必填 | 服务器支持的远端文件名/路径，不是本地磁盘路径；示例文件名只演示调用方式。 |
| `index` | `int` | 必填 | 分片编号；完整下载由客户端从 1 递增。 |
| `offset` | `int` | 必填 | 协议偏移；文件接口为字节偏移，K 线索引接口为索引请求偏移。 |
| `size` | `int` | 必填 | 本次请求的分片字节数。 |

## 使用示例

示例代码用于展示调用方式。

```python
from eltdx.mac import MacClient

with MacClient() as client:
    result = client.download_file_chunk("tdxhy.cfg", index=1, offset=0, size=30000)
    print(result)
```

## 分页、单位与限制

返回 bytes，不写本地文件、不自动解码、不验证整文件哈希。offset/size 单位字节，index 为请求片号。读到短分片要结合元信息判断结束或数据不完整。

## 返回字段

返回分片内容的 bytes；空内容需结合预期文件长度解释。

## 来源与相关文档

签名与行为依据当前仓库 `src/eltdx/mac/client.py` 及对应命令解析器；本页未标注实测的市场覆盖不作线上成功承诺。

- [完整接口索引](README.md)
- [枚举与字段位图](枚举与字段位图.md)
- [返回模型](返回模型.md)
- [主机能力与通道概览](../EXTENDED_MARKET.md)
