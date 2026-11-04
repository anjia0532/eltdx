---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# MAC-EX 连接与主机管理

MacExClient 是同步客户端，端口默认 7727。建议以 with 管理连接生命周期，避免在多个线程上同时复用同一个请求连接。

## __init__

```text
MacExClient.__init__(host: str | None=None, port: int=DEFAULT_EX_PORT, timeout: float=15.0, *, hosts: list[str] | None=None) -> None
```

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `host` | `str \| None` | `None` | 优先主机的裸地址；MAC 的 hosts 非 None 时优先使用 hosts，EX/MAC-EX 将 host 置于候选首位。 |
| `port` | `int` | `DEFAULT_EX_PORT` | TCP 端口；MAC 默认 7709，EX/MAC-EX 默认 7727。 |
| `timeout` | `float` | `15.0` | 读写或探活超时，单位秒。 |
| `hosts` | `list[str] \| None` | `None` | 候选主机列表；省略时使用各客户端自己的内置/配置主机池。 |

构造/返回客户端实例；实际业务仍须确认目标主机支持所需命令。from_best_host 选主机，不把所有协议能力探测一遍。

## from_best_host

```text
MacExClient.from_best_host(hosts: list[str] | None=None, port: int=DEFAULT_EX_PORT, timeout: float=15.0, ping_timeout: float=5.0) -> 'MacExClient'
```

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `hosts` | `list[str] \| None` | `None` | 候选主机列表；省略时使用各客户端自己的内置/配置主机池。 |
| `port` | `int` | `DEFAULT_EX_PORT` | TCP 端口；MAC 默认 7709，EX/MAC-EX 默认 7727。 |
| `timeout` | `float` | `15.0` | 读写或探活超时，单位秒。 |
| `ping_timeout` | `float` | `5.0` | 选择主机时探活超时，单位秒。 |

构造/返回客户端实例；实际业务仍须确认目标主机支持所需命令。from_best_host 选主机，不把所有协议能力探测一遍。

## ping_all

```text
MacExClient.ping_all(hosts: list[str] | None=None, port: int=DEFAULT_EX_PORT, timeout: float=5.0) -> list[tuple[str, float]]
```

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `hosts` | `list[str] \| None` | `None` | 候选主机列表；省略时使用各客户端自己的内置/配置主机池。 |
| `port` | `int` | `DEFAULT_EX_PORT` | TCP 端口；MAC 默认 7709，EX/MAC-EX 默认 7727。 |
| `timeout` | `float` | `5.0` | 读写或探活超时，单位秒。 |

返回按延迟升序的 (host, seconds) 列表，延迟单位秒；不要把探活成功等同于所有市场/命令可用。

## connect

```text
MacExClient.connect() -> None
```

无业务参数。

返回 None。connect 建立连接，close 释放连接；disconnect 是 close 的语义别名。ensure_connected 的实际检查范围见下节。

## close

```text
MacExClient.close() -> None
```

无业务参数。

返回 None。connect 建立连接，close 释放连接；disconnect 是 close 的语义别名。ensure_connected 的实际检查范围见下节。

## disconnect

```text
MacExClient.disconnect() -> None
```

无业务参数。

返回 None。connect 建立连接，close 释放连接；disconnect 是 close 的语义别名。ensure_connected 的实际检查范围见下节。

## ensure_connected

```text
MacExClient.ensure_connected() -> None
```

无业务参数。

返回 None。connect 建立连接，close 释放连接；disconnect 是 close 的语义别名。ensure_connected 的实际检查范围见下节。

## 主机、重试与属性

默认 MAC_EX_HOSTS，不使用普通 EX 配置池；每次连接后执行 0x2454 登录。ensure_connected 只在 _connected 为 False 时建连，并非每次发心跳验证。业务请求 TransportError 时重连、重新登录并重试一次；当前主机仍排在候选首位，不能保证失败后一定切换到别台。当前没有公开 host/healthy_hosts 属性。

## 使用示例

```python
from eltdx.ex import MacExClient

with MacExClient() as client:
    result = client.instruments(33, count=5)
    print(result)
```

## 错误处理

传输失败通过 TransportError 及其子类传播，协议解码失败可抛 ProtocolError；参数检查也可能抛 ValueError、TypeError 或 struct.error，当前并未统一封装所有参数错误。空列表/None/0 也需根据单页规则解释，不把缺数据当作请求成功且覆盖完整。

[返回完整索引](README.md) · [主机覆盖与配置](../EXTENDED_MARKET.md)
