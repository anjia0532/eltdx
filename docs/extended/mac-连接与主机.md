---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC 连接与主机管理

MacClient 是同步客户端，端口默认 7709。建议以 with 管理连接生命周期，避免在多个线程上同时复用同一个请求连接。

## __init__

```text
MacClient.__init__(host: str | None=None, port: int | None=None, timeout: float | None=None, hosts: Sequence[str] | None=None, *, socket_factory: SocketFactory | None=None, xdxr_provider: XdxrProvider | None=None) -> None
```

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `host` | `str \| None` | `None` | 优先主机的裸地址；MAC 的 hosts 非 None 时优先使用 hosts，EX/MAC-EX 将 host 置于候选首位。 |
| `port` | `int \| None` | `None` | TCP 端口；MAC 默认 7709，EX/MAC-EX 默认 7727。 |
| `timeout` | `float \| None` | `None` | 读写或探活超时，单位秒。 |
| `hosts` | `Sequence[str] \| None` | `None` | 候选主机列表；省略时使用各客户端自己的内置/配置主机池。 |
| `socket_factory` | `SocketFactory \| None` | `None` | 测试或自定义传输使用的 socket 工厂；普通调用保持 None。 |
| `xdxr_provider` | `XdxrProvider \| None` | `None` | (market, code) -> Sequence[XdxrEvent] 或 None 的回调，用于 MAC 前复权非法价格的本地兜底。 |

构造/返回客户端实例；实际业务仍须确认目标主机支持所需命令。from_best_host 选主机，不把所有协议能力探测一遍。

## from_best_host

```text
MacClient.from_best_host(hosts: Sequence[str] | None=None, port: int | None=None, timeout: float | None=None, ping_timeout: float=5.0) -> MacClient
```

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `hosts` | `Sequence[str] \| None` | `None` | 候选主机列表；省略时使用各客户端自己的内置/配置主机池。 |
| `port` | `int \| None` | `None` | TCP 端口；MAC 默认 7709，EX/MAC-EX 默认 7727。 |
| `timeout` | `float \| None` | `None` | 读写或探活超时，单位秒。 |
| `ping_timeout` | `float` | `5.0` | 选择主机时探活超时，单位秒。 |

构造/返回客户端实例；实际业务仍须确认目标主机支持所需命令。from_best_host 选主机，不把所有协议能力探测一遍。

## ping_all

```text
MacClient.ping_all(hosts: Sequence[str] | None=None, port: int | None=None, timeout: float=5.0) -> list[tuple[str, float]]
```

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `hosts` | `Sequence[str] \| None` | `None` | 候选主机列表；省略时使用各客户端自己的内置/配置主机池。 |
| `port` | `int \| None` | `None` | TCP 端口；MAC 默认 7709，EX/MAC-EX 默认 7727。 |
| `timeout` | `float` | `5.0` | 读写或探活超时，单位秒。 |

返回按延迟升序的 (host, seconds) 列表，延迟单位秒；不要把探活成功等同于所有市场/命令可用。

## connect

```text
MacClient.connect() -> None
```

无业务参数。

返回 None。connect 建立连接，close 释放连接；disconnect 是 close 的语义别名。ensure_connected 的实际检查范围见下节。

## close

```text
MacClient.close() -> None
```

无业务参数。

返回 None。connect 建立连接，close 释放连接；disconnect 是 close 的语义别名。ensure_connected 的实际检查范围见下节。

## disconnect

```text
MacClient.disconnect() -> None
```

无业务参数。

返回 None。connect 建立连接，close 释放连接；disconnect 是 close 的语义别名。ensure_connected 的实际检查范围见下节。

## ensure_connected

```text
MacClient.ensure_connected() -> None
```

无业务参数。

返回 None。connect 建立连接，close 释放连接；disconnect 是 close 的语义别名。ensure_connected 的实际检查范围见下节。

## 主机、重试与属性

默认 MAC_HOSTS，协议通常使用 0x1c 帧，0x1218 等有专用 head_flag。hosts 非 None 时覆盖 host；host 属性为当前主机，hosts 为候选副本。connect 会握手。ensure_connected 用 KlineOffsetCmd 业务请求检查存活；请求失败时关闭并换候选重试一次。没有后台心跳线程，也没有 auto_reconnect / heartbeat_interval 参数。

## 使用示例

```python
from eltdx.mac import MacClient

with MacClient() as client:
    result = client.get_server_info()
    print(result)
```

## 错误处理

传输失败通过 TransportError 及其子类传播，协议解码失败可抛 ProtocolError；参数检查也可能抛 ValueError、TypeError 或 struct.error，当前并未统一封装所有参数错误。空列表/None/0 也需根据单页规则解释，不把缺数据当作请求成功且覆盖完整。

[返回完整索引](README.md) · [主机覆盖与配置](../EXTENDED_MARKET.md)
