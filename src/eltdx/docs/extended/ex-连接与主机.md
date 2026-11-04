---
hide:
  - navigation
---

[← 返回接口目录](../index.md){ .interface-detail-back }

# EX 连接与主机管理

ExTdxClient 是同步客户端，端口默认 7727。建议以 with 管理连接生命周期，避免在多个线程上同时复用同一个请求连接。

## __init__

```text
ExTdxClient.__init__(host: str | None=None, port: int=DEFAULT_EX_PORT, timeout: float=15.0, *, hosts: list[str] | None=None, auto_failover: bool=True, probe_on_connect: bool=True, probe_timeout: float | None=None, max_probe_workers: int=DEFAULT_PROBE_WORKERS) -> None
```

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `host` | `str \| None` | `None` | 优先主机的裸地址；MAC 的 hosts 非 None 时优先使用 hosts，EX/MAC-EX 将 host 置于候选首位。 |
| `port` | `int` | `DEFAULT_EX_PORT` | TCP 端口；MAC 默认 7709，EX/MAC-EX 默认 7727。 |
| `timeout` | `float` | `15.0` | 读写或探活超时，单位秒。 |
| `hosts` | `list[str] \| None` | `None` | 候选主机列表；省略时使用各客户端自己的内置/配置主机池。 |
| `auto_failover` | `bool` | `True` | 是否开启 EX 命令级失败换台。 |
| `probe_on_connect` | `bool` | `True` | 是否在 EX 连接前探测候选主机的业务应答。 |
| `probe_timeout` | `float \| None` | `None` | EX 业务探活超时；None 时由当前 timeout 与默认探活上限共同决定。 |
| `max_probe_workers` | `int` | `DEFAULT_PROBE_WORKERS` | EX 探活最大并发数。 |

构造/返回客户端实例；实际业务仍须确认目标主机支持所需命令。from_best_host 选主机，不把所有协议能力探测一遍。

## from_best_host

```text
ExTdxClient.from_best_host(hosts: list[str] | None=None, port: int=DEFAULT_EX_PORT, timeout: float=15.0, ping_timeout: float=DEFAULT_PROBE_TIMEOUT) -> 'ExTdxClient'
```

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `hosts` | `list[str] \| None` | `None` | 候选主机列表；省略时使用各客户端自己的内置/配置主机池。 |
| `port` | `int` | `DEFAULT_EX_PORT` | TCP 端口；MAC 默认 7709，EX/MAC-EX 默认 7727。 |
| `timeout` | `float` | `15.0` | 读写或探活超时，单位秒。 |
| `ping_timeout` | `float` | `DEFAULT_PROBE_TIMEOUT` | 选择主机时探活超时，单位秒。 |

构造/返回客户端实例；实际业务仍须确认目标主机支持所需命令。from_best_host 选主机，不把所有协议能力探测一遍。

## ping_all

```text
ExTdxClient.ping_all(hosts: list[str] | None=None, port: int=DEFAULT_EX_PORT, timeout: float=DEFAULT_PROBE_TIMEOUT) -> list[tuple[str, float]]
```

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `hosts` | `list[str] \| None` | `None` | 候选主机列表；省略时使用各客户端自己的内置/配置主机池。 |
| `port` | `int` | `DEFAULT_EX_PORT` | TCP 端口；MAC 默认 7709，EX/MAC-EX 默认 7727。 |
| `timeout` | `float` | `DEFAULT_PROBE_TIMEOUT` | 读写或探活超时，单位秒。 |

返回按延迟升序的 (host, seconds) 列表，延迟单位秒；不要把探活成功等同于所有市场/命令可用。

## connect

```text
ExTdxClient.connect() -> None
```

无业务参数。

返回 None。connect 建立连接，close 释放连接；disconnect 是 close 的语义别名。ensure_connected 的实际检查范围见下节。

## close

```text
ExTdxClient.close() -> None
```

无业务参数。

返回 None。connect 建立连接，close 释放连接；disconnect 是 close 的语义别名。ensure_connected 的实际检查范围见下节。

## refresh_hosts

```text
ExTdxClient.refresh_hosts(*, timeout: float | None=None, max_workers: int | None=None) -> list[ExHostProbe]
```

| 参数 | 类型 | 默认值 | 含义 |
| --- | --- | --- | --- |
| `timeout` | `float \| None` | `None` | 读写或探活超时，单位秒。 |
| `max_workers` | `int \| None` | `None` | 重探时覆盖 EX 探活并发数；None 沿用实例配置。 |

返回 ExHostProbe 列表并更新健康排序。成员为 host、ok、latency_ms（毫秒，可为 None）、error（错误文本，可为 None）；失败原因也可从 unhealthy_hosts 查看。

## 主机、重试与属性

候选来自显式 hosts、ELTDX_EX_HOSTS、用户 ex_servers.json 或内置池，host 放在首位；环境变量及配置规则见通道概览。业务探活默认 0x23F5，单候选不额外探活。auto_failover 开启时，TransportError 触发健康标记与候选切换。host 是当前/待用主机，healthy_hosts 为可用列表副本，unhealthy_hosts 为主机到失败原因字典；空健康列表可能表示尚未探测。

## 使用示例

```python
from eltdx.ex import ExTdxClient

with ExTdxClient() as client:
    result = client.get_instrument_count()
    print(result)
```

## 错误处理

传输失败通过 TransportError 及其子类传播，协议解码失败可抛 ProtocolError；参数检查也可能抛 ValueError、TypeError 或 struct.error，当前并未统一封装所有参数错误。空列表/None/0 也需根据单页规则解释，不把缺数据当作请求成功且覆盖完整。

[返回完整索引](README.md) · [主机覆盖与配置](../EXTENDED_MARKET.md)
