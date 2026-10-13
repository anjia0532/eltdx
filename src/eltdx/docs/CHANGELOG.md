# 变更记录

## v3.4.0 - 2026-10-13

### 新增

- **7615 免登录 F10 接口合并为 8 个 section 驱动方法**：`F10Client` 新增 `shareholders`（11 个分区）、`capital_structure`（5）、`business_report`（6）、`industry_analysis`（10）、`trading_report`（11）、`fund_report`（30）、`market_report`（20）、`digest`（8），把个股 F10（`CWServ.tdxf10_gg_*`）、ETF / 场外基金（`CWServ.skef10_jj_*`）、板块 / 指数（`skef10_bk_*` / `skef10_zs_*`）、大盘（`skef10_dpzx_*`）的多页面分区收敛成 8 个入口。个股、ETF 基金、板块、指数、大盘**共用同一批方法**，靠 `section` 分派，不为每种标的类型另开 API；全部是纯 HTTP POST 到 `http://static.tdx.com.cn:7615/TQLEX`，不需要 7709 握手或登录。
- 既有方法只补 `section`、不新增同义方法：`profit_forecast()` 新增 `ylyctj` / `ylycmx` / `yzyq` / `tzpjtj` / `ycpjyjbg`；`industry_analysis()` 新增 `comparable` / `comparable_profile`（走 `CWServ.tdxf10_gg_kbgs`）；`company_news()` 新增 `finance_review`（走 `CWServ.tdxf10_gg_cwfx_cbdp`）；`shareholder_change_plans()` 委托给 `shareholders(code, section="plan")`；`business_composition()` 委托给 `business_report(code, "composition", report_date=...)`。未知 `section` 一律抛 `ValueError` 并列出全部合法取值。
- **`eltdx f10` 子命令**：新增 `eltdx f10 <action> [CODE] --section/--arg/--date/--report-date/--topic/--entry/--params/--page/--page-size`，25 个 action 覆盖上述方法与既有 F10 页面；`eltdx f10 sections` 不联网列出全部合法 `--section`（含默认值），`eltdx f10 call --entry ... --params '[...]'` 可直接调用任意 Entry。
- 文档新增 6 个接口详情页（股东研究 / 股本结构 / 行业分析 / 交易数据 / 基金与 ETF / 板块与指数），`F10_7615.md` 补三节 Entry 对照表（个股其余 Entry、`skef10_jj_*` 的 7 个菜单页与 13 个 Entry、`skef10_bk_*` / `skef10_zs_*` / `skef10_dpzx_*` 的菜单与 Entry 对照），README 功能地图与新章节同步补齐。

### 行为变更

- **`client.money_flow.history()` 改走 7615，不再使用 7709 category 22**：签名变为 `history(code, *, days=60, start=0, count=None, include_raw=False, batch_size=75)`，底层请求 `CWServ.tdxf10_gg_sj` 的 `{"Params": ["zjlx_sj", code, str(days), code]}`（`days` 只接受 `3` / `5` / `10` / `20` / `60`），返回新的 `eltdx.models.money_flow.FundFlowRangeSeries`（已由 `eltdx.models` 导出），`start` / `count` 变成拿到响应后的客户端切片。旧的 7709 `0x052d` category 22 通路实测在 18 台可达主站（普通池 + 资金流向专用池）上一律返回 2 字节 `0000` 空 payload，已废弃；`period="flow"` 不再有效，`client.bars.get(..., period="flow")` 抛 `ValueError`。旧 DTO `FundFlowHistorySeries` / `FundFlowHistoryRecord` 仍在 Rust 侧导出，但已不是本方法的返回值。
- `eltdx money-flow` 增加 `--days 3|5|10|20|60`：不传仍走 7709 `0x0ffc` 当日分档，传了走 7615 区间通道。
- `-o table / csv / jsonl` 会把 TQLEX 回包展开成数据行（多结果集按顺序拼接）；默认的 `-o json` 仍保留完整回包（`entry` / `request_body` / `result_sets` / `raw`），便于排查。
- `eltdx f10 detail` 现在需要两个位置参数（`detail_type` 与 `record_id`）：`eltdx f10 detail xw 22075813`。
- 接口目录的 7615 层从 22 项扩到 28 项（`docs/index.md` 的 7615 说明同步改成 27 个功能调用），功能目录新增 `交易数据`、`基金与市场` 两个分类。

### 修复内容

- `fund_report(section="finance")` 的默认取表由 `cwzb` 改为 `zcfzb`：实测 `cwzb` 对 ETF 返回 0 行，`zcfzb`（资产负债表）返回 28 行。
- `bars.get(..., period="flow")` 的报错信息不再提及已废弃的 `0x052d` category 22 与 `count=`，改为指向 `money_flow.history(code, days=...)`。
- README 补齐 3.3.0 / 3.3.1 已发布但从未记录的通路：扩展行情 7727、场外基金、MAC 协议、本地行情文件（vipdoc）、公司信息文本 F10（`0x02cf` / `0x02d0` / `0x02c5`）、`eltdx.Market` 枚举与 `bar_time`，并列出 `eltdx ex` / `fund` / `mac` / `offline` 命令行入口；同时修正 README 的「21 个 7709 命令」为 25、`ARCHITECTURE.md` 的 registry 计数 22 → 25。

## v3.3.1 - 2026-10-12

### 新增

- MCP 的公司概况、热点题材、财务报表和公司资讯 F10 结果新增按 Entry / 请求分区解析的 `field_labels`、`unmapped_fields` 与 `field_notes`；资产负债表、利润表和现金流量表进一步按 `nhytype` 区分通用企业、银行、券商和保险模板，保留原始字段和行结构，避免 `T039` 等跨接口或跨行业字段被错误复用。
- 财务报表字段映射补充保险保费/赔付项目、金融行业专用现金收支和现金流量补充资料；确认通用企业现金流量表 `T063` 是不承载数值的分组标题。银行历史现金流量表 `T088` 是随证券和报告期变化的动态扩展项，继续显式未映射，并通过 `field_notes` 返回歧义说明。

### 修复

- **客户端资源延迟回收（引用环）**：`TdxClient` 与它的子服务此前互持强引用——子服务持有 client 的 bound method（`price_resolver` / `metadata_sink` / `transport_factory`），client 又持有这些子服务，构成引用环，引用计数永远到不了 0，底层 Rust worker 线程只能等分代 GC 才回收。实测（关闭 gc）10 个未 `close()` 的客户端会滞留约 **5 条线程/个**；现在**每个 0 条**，`del` 后立即释放。做法：子服务改为持弱引用（bound method 用 `weakref.WeakMethod`，其余用 `weakref.ref`），`TdxClient` 显式声明 `__weakref__` 槽位使其可被弱引用。
- **扩展行情并发探活早退不再残留线程**：`probe_ex_hosts(stop_after_first=True)` 此前用 `shutdown(wait=False)`，被放弃的在途探活线程要等满 `probe_timeout` 才退出——实测 6 次创建客户端会累积到 **97 条 OS 线程**。现在早退时**主动中断**在途连接（关闭其 socket，使阻塞中的 `connect()` 立即失败）后再 `shutdown(wait=True)`：同样场景回落到 **5 条**，而 connect 耗时仍是 **0.08 秒**。

### 行为变更

- **`TdxClient(...).helpers.foo()` 这类临时链式调用不再可用**：打断引用环的同时也取消了「子服务替 client 续命」的副作用，因此不绑定到变量就直接链式调用会抛 `ReferenceError`。请先 `client = TdxClient(...)` 再调用——文档与全部示例一直是这样写的，`with TdxClient() as client:` 不受影响。

## v3.3.0 - 2026-10-12

> **兼容性说明**：以下「移除」与「行为变更」两节涉及的模块
> （`eltdx.offline`、`eltdx.ex.mac_commands`、`MacExClient`、`MacClient.get_stock_kline`
> 的帧格式）都是 `7057088` 起新增、且**从未随任何正式版本发布过**的代码。
> `v3.2.3` 及更早版本不含它们，因此从 `v3.2.3` 升级到 `v3.3.0` 的普通使用者
> **不受这些改动影响**；只有直接跟踪 `main` 分支、已经在用这些未发布 API 的人需要关注。

### 修复

- **`MacClient.get_stock_kline()` 完全不可用**：`SymbolBarCmd` 帧体少 1 个标志字节（`bbb` 应为 `bbbb`），服务端对任何标的都只回 1 字节空体，随即抛 `ProtocolError: symbol_bar header: 数据不足，需要 9 字节`。已在 7709 与 7727 两条通道上分别验证：修复前两个市场均失败，修复后 `MacClient.get_stock_kline(0, "000001")` 正常返回 K 线。
- **本地行情文件读取过于严格**：`.day` / `.lc1` / `.lc5` / `.5` / 扩展市场 `.day` 现在只遍历完整记录，末尾不足一条的残尾被忽略，文件不足一条记录时返回空列表。此前残尾会抛 `ResourceFormatError`，使通达信写盘中断留下的截断文件整份读不出来；现与 `easy_tdx` 行为一致。
- **港股 `ds/*.day` 的成交额口径错误**：该槽位存的是 `float32`，按整数读会得到 IEEE-754 位模式（`1234567.5` → `1234613308`）。`ExDailyBar` 新增 `hk_stock_amount` 字段给出正确值（与 `easy_tdx` 同名同值，已用同一份合成文件逐条对照通过）；`amount` 保留整数视图，写回时使用它，读改写不丢字节。
- **`normalize_code` 缺 `5xxxxx` 号段**：沪市 ETF / LOF / 货币基金 / 权证（`510300`、`511360`、`515180`、`518850`、`501050`、`580000` 等）此前会抛 `ProtocolError: unable to infer market`，现正确识别为沪市；同时补上 `4xxxxx` → 北交所（`430047`），与既有的 `92xxxx` → 北交所、`900xxx` → 沪市 B 股规则保持一致。
- **省略端口的主机被静默丢弃**：`normalize_host` 此前要求 host 必须含 `:`，于是 `TdxClient(host="116.205.183.150")`、`TdxClient(hosts=["10.0.0.1"])` 这类写法会被逐条丢弃，最终只报一句 `at least one host is required`——用户看到的是「缺少主机」，而实际输入里明明有主机。现在省略端口时**自动补 7709**，并用 `DEFAULT_QUOTE_PORT` 常量导出；`normalize_host(..., default_port=None)` 可恢复「必须显式给端口」的严格模式。`"116.205.183.150"` 与 `"116.205.183.150:7709"` 会被归一成同一条，避免同一主机被重复连接。
- **裸 IPv6 被错误解析**：`"::1"` 原先按 `rsplit(":", 1)` 拆成 `host=":"`、`port="1"`，得到一个无意义的 `":1"`。现在裸 IPv6 会补上方括号规整为 `"[::1]:7709"`，且规整结果**幂等**（再次规整不变）。
- **`at least one host is required` 信息不具可操作性**：现在附上正确写法示例与「端口默认 7709」的说明；MCP 的 `host` 参数校验也从 `host must use host:port with a port between 1 and 65535` 改为说明端口可省略。
- **`ExTdxClient` 的故障转移形同虚设，导致扩展行情「查不到」场外基金**：旧 `_execute()` 失败后调用 `connect()`，而 `connect()` 依据的 `_ordered_hosts()` 把**当前这台（刚失败的）主机排在首位**，于是重连又回到同一台、再次失败。更根本的是失败判定只看 TCP，而 16 台内置主机 **TCP 全部可连**、只有极少数会应答业务命令，所以换台条件永远不会成立。实测默认 `ExTdxClient()` 调 `get_instrument_info()` 必然超时，`016947`（国泰利安中短债A，`market=33`、`category=8`）这类场外基金因此查不到——**根因不是「场外基金不收录」**，也不是协议错误。

### 移除

- **删除 `ExTdxClient.send_setup()` 与 `eltdx.ex.commands.setup`**：该握手帧是从 `easy_tdx` / `pytdx` 移植过来的、上游从未调用的常量；被包装成公开方法后，调用它会让服务器回一帧恒定 299 字节，之后对任何命令都不再应答，等于把连接打死。`connect()` 从不调用它，库内也无其他引用，删除后无行为影响。
- `eltdx.ex.mac_commands` **不再重复定义命令类**，改为再导出 `eltdx.mac.commands` 的同一批实现（与 `eltdx.ex.mac_models` 相同的薄转发模式）。两份副本此前已各自漂移，并因此产生了上面的 `SymbolBarCmd` 缺陷。

### 行为变更

- `eltdx.ex.mac_commands` 的 `Period` / `Adjust` 现为 `eltdx.mac.enums` 中的同一对象（成员与取值不变，仅类型标识统一）。
- `SymbolBarCmd` 的 `times` 参数改为 keyword-only 并移到参数表末尾，恢复 `(market, code, period, start, count, fq)` 的位置传参顺序——此前 `SymbolBarCmd(47, "IFL0", Period.DAILY, 0, 800)` 会把 `0`/`800` 错位成 `times`/`start`。
- `MacExClient.goods_quotes()` / `goods_quotes_list()` 的默认请求字段仍是原先的 7 个基础字段（前收/开/高/低/收/量/额），请求字节与返回值不变；该默认值现由 `eltdx.ex.mac_commands.DEFAULT_QUOTE_FIELDS` 显式给出。
- **`eltdx ex markets` 不再默认向服务器索取市场表**：改用 `--probe-server` 才走网络。实测所有内置主站都不回应 `get_markets`（`0x23f4`），原行为是每台主机各等满一个连接超时（默认 2 台 = 约 30 秒）后才回退到枚举，而**枚举本身就是完整且权威的市场表**——实测该命令耗时 **30.6 秒 → 0.3 秒**，输出逐字节不变。判定依据：eltdx 与 easy_tdx 1.20.7 的 `GetExMarketsCmd` 请求帧完全相同（`01 02 48 69 00 01 02 00 02 00 f4 23`），同一主机上 easy_tdx 同样超时，且同一连接上 `get_instrument_count()` 在两边都正常返回 `107165`，故属服务端行为而非本项目缺陷。

### 新增

- **`bar_time` 时间戳语义（对齐 easy_tdx）**：`client.bars.get()`、`ExTdxClient.get_instrument_bars()`、`ExTdxClient.get_history_instrument_bars_range()`、`MacClient.get_stock_kline()` 新增关键字参数 `bar_time`，默认 `"start"`（通达信原始：上午最后一根 5min 标 `11:25`、下午第一根标 `13:00`）；传 `"end"` 则给**分钟级** bar 加上一个周期时长得到右端点（同一根标 `11:30`），与 Tushare/同花顺对齐。日线及以上、多日、秒级周期一律不偏移（不影响任何日线调用）。`get_history_instrument_bars_range` 与 easy_tdx 一样**不支持 `"end"`**——它只按日期范围查询、拿不到周期时长，会抛 `ValueError` 而不是静默返回错值；非法取值同样 fail-fast。三条路径的进位语义分别与 easy_tdx 逐条对拍通过：扩展行情按 `hour/minute` 的 `% 24` 回绕、MAC 按真实 `timedelta`（可跨日）、7709 按 `% 24` 回绕。周期到分钟数的换算取自各协议自身的编号（扩展行情 `KlineCategory`、MAC `Period`、7709 `KlinePeriod`），其中 7709 直接复用响应里已解析好的 `period_raw`/`period_param_raw`，避免重复实现映射而与 Rust 侧漂移。
- **`eltdx.Market` 枚举**（与 `easy_tdx.models.enums.Market` 同名同路径）：`SZ=0` / `SH=1` / `BJ=2`，并带 `code` 属性返回 `"sz"/"sh"/"bj"`。`eltdx` 内部仍以小写字符串为准，两者可互换传给任何 `market` 参数。`tests/test_protocol_unit.py` 会断言它与 `MARKET_TO_ID` 一致，防止两处漂移。
- **`MacExClient.goods_quotes_list()` 的 `sort_type` / `sort_order` 恢复位置传参**：以前是 keyword-only，`goods_quotes_list(33, 0, 5, SortType.CHANGE_PCT, SortOrder.DESC)` 会报 `TypeError`；现在与 `easy_tdx` 一致，并接受普通 `int`。注意这两个参数**仅作预留、不生效**——底层 `GoodsListCmd`（0x2562）请求体只有 `market/start/count`，协议上无法排序（`easy_tdx` 亦标注为「暂未实现排序」）。
- **6 个扩展行情模型补齐 `_raw`**：`ExInstrumentBar` / `ExInstrumentInfo` / `ExInstrumentQuote` / `ExMarketInfo` / `ExMinuteBar` / `ExTransactionRecord` 现在都带 `_raw: bytes`，保存该条记录在响应体中的**原始字节切片**（与 `easy_tdx` 同名同语义）。7 个构造点全部填充，切片范围与 `easy_tdx` 逐一对齐。该字段 `repr=False`、`compare=False` 且有默认值 `b""`，因此**不参与相等比较、不出现在 repr、也不破坏既有位置/关键字构造**。用途：本库尚未解析的字段可以按字节级复核，不用重发请求。
- **`MacClient.ping_all()` / `MacClient.from_best_host()`**（对应 `easy_tdx` 同名 API）与底层 `eltdx.mac.ping_mac_all` / `ping_mac_host`。`from_best_host` 会把探测到的最快主机放到候选列表**首位**，因此 `client.host` 确实是那台最快的主机，其余候选保留用于故障转移。
- **`MacClient.ensure_connected()`**（对应 `easy_tdx` 同名 API）：用一条极廉价的 `KlineOffsetCmd(0, 1)` **真实探测**连接，断线则重建。这里刻意不只看标志位——标志位发现不了「TCP 还在但服务端已经不理人」的半开连接。传输失败时沿用 `_execute` 既有的故障转移，会把当前主机切到候选列表下一台并重试。
- **`ExTdxClient` 并发探活 + 失败自动负载均衡**：`connect()` 现在用真实业务命令（默认枚举命令 `0x23f5`）**并发**探测全部候选主机，只把真正应答的按延迟排到前面。失败判定改为**命令级**（拿到应答才算成功）：失败主机立即被排除出候选，请求自动落到其余健康主机；成功一次即恢复其健康标记；全部失败时清空标记重来一轮，避免会话被永久锁死。失败后还会**并发重探**剩余主机，因此一次失败不会退化成 `15 × timeout` 的串行盲试。探活采用**首个可用即返回**的早退策略——实测默认 `ExTdxClient()` 的 `connect()` 由「必然失败」变为 **0.08 秒**（等满完整探活要 3 秒，串行则要 15 次超时）。单主机模式（只给 `host`，或 `hosts` 只有一台）**不探活**，与旧版行为一致、零额外开销。新增 `healthy_hosts` / `unhealthy_hosts` 属性与 `refresh_hosts()` 方法，以及 `auto_failover` / `probe_on_connect` / `probe_timeout` / `max_probe_workers` 参数；`hosts=[]` 现在明确报 `ValueError`（旧代码把「显式要零台」当成「未指定」而静默回退到全部内置主机）。
- **`ExTdxClient.ping_all()` / `from_best_host()` 语义修正**：旧版把「TCP 能连上」当成健康，于是 16 台内置主机**全部**返回、`from_best_host()` 实际等于随机挑一台。现在探活要求主机真的应答业务命令，`ping_all()` 实测只返回 **1/16**，选出来的主机确实可用；`from_best_host()` 会把自己探到的排名直接交给客户端，不再重复探活。底层新增 `probe_ex_host()` / `probe_ex_hosts()` / `rank_ex_hosts()` 与 `ExHostProbe`。
- **扩展行情主机表的用户可覆盖配置层**：新增环境变量 `ELTDX_EX_HOSTS` 与用户配置文件 `<data_dir>/ex_servers.json`，优先级为 **环境变量 > 用户配置 > 包内默认**，因此**不发版也能替换主机表**。配套 `load_ex_hosts()` / `load_ex_hosts_from_env()` / `load_ex_hosts_from_file()` / `save_ex_hosts()` / `ex_server_file_path()` / `normalize_ex_host()`，跨平台数据目录抽到 `eltdx._paths.data_dir()`（`ELTDX_DATA_DIR` 可覆盖，与安装包分离故重装/升级不覆盖）。主机项写**裸主机名/IP**，端口由 `ExTdxClient(port=)` 统一指定（默认 7727），写成 `host:port` 会明确报错而不是静默忽略；配置非法（JSON 坏、缺 `hosts`、条目无效）**立刻抛 `ValueError`**，不会静默回退到默认列表。
- **扩展行情默认主机顺序调整**：新增 `DEFAULT_EX_HOSTS`，把逐台实测后**唯一能应答枚举命令 `0x23f5`** 的主机（`PROBE_VERIFIED_EX_HOSTS`）排在官方顺序之前。实测能力矩阵：`0x23f0`（商品总数）**16/16** 应答，`0x23f5`（枚举）**1/16**，`0x23fa`（报价）/ `0x23ff`（K 线）**0/16** —— 所以「只按 TCP 或只按 `0x23f0` 探活」没有任何区分度，这也是旧版选主失效的实测依据。`KNOWN_EX_HOSTS` 保持通达信官方 `[DSHOST]` 的顺序不变，作为来源记录。

- **资金流空数据主机故障转移**：`money_flow.daily()` 拿到的直连结果为空时，不再立刻返回空，
  而是按已排好的延迟顺序**逐台主机实测**，拿到非空即返回；**所有主机都为空时返回空而不是抛错**
  （新股 / 真无数据的标的不能被误报成故障）。找到可用主机后会记住并复用，避免每次空返回都重探。
  重试次数有上界：一次 `daily()` 调用只探测一轮，整批共享，不会出现「一批 75 只空票 × 候选主机数」的连接放大。
  该行为只在响应**确实是空数据**（带 `blocks` 且为空）时触发；只有非连接池客户端（无候选主机）时自动退化为原行为。

### 内部

- **MAC 选主探测要求「服务器给出交易日」**，不能只看「没抛异常」：`ServerInfoCmd.parse_response` 对短于 87 字节的响应体是宽容的，会返回 `ServerSession(today="")` 而不报错，所以 `ping_mac_host` 额外要求 `today` 非空。否则端口开放但不提供 MAC 行情的主机会被误选为最佳节点。已对真实服务器验证：`today='2026-10-12'`，判定通过。
- **`BaseCommand` 统一为单一类对象**：`eltdx.mac.commands` 与 `eltdx.ex.commands.base` 此前各定义了一个结构相同、仅 TypeVar 名不同的基类，导致把 MAC 命令交给 `MacExClient._execute`（形参标注为 *ex* 的 `BaseCommand`）时被类型检查判为不兼容（9 处错误）。现统一到 :mod:`eltdx._command`，两个模块只做再导出。
- **25 个 7709 命令全部有差分 fixture**：`block_meta`（`0x02c5`）、`company_info_category`（`0x02cf`）、`company_info_content`（`0x02d0`）补齐后，`tests/native/test_differential.py` 的 `PENDING_DIFFERENTIAL_FIXTURES` 已清空为 `frozenset()`，`tests/contracts/test_static_fixture_inputs.py` 的期望清单从 22 个命令更新到 25 个。这 3 个 fixture 的输入由 `scripts/fixtures/materialize_static_inputs.py` **离线合成**（无需连服务器），载荷格式取自 `crates/eltdx-protocol/src/commands/{corporate,resources}.rs` 的常量与解析器：板块元数据 38 字节 = `size`(u32 LE) + 1 保留字节 + 32 字节 ASCII md5；公司信息目录 = `count`(u16 LE) + `count × 152` 字节记录（64 name + 80 filename + 4 start + 4 length，GBK）；公司信息内容 = 12 字节头（正文长度在 `[10:12]`）+ GBK 正文。
- **`_native` 可从本仓库源码在 Windows 上本地编译**：用 MinGW-w64（`gcc 16.2.0`）+ `rustc 1.99.0 (x86_64-pc-windows-gnu)`，`cargo build --release -p eltdx-python` 约 42 秒产出 `_native.dll`（约 5.9 MB），复制为 `src/eltdx/_native.pyd` 即可（该路径已被 `.gitignore` 忽略）。编译产物与 `v3.2.3` 发布版二进制**行为零回归**（全量测试结果逐项相同），并额外支持上述 3 个新命令。注意：`crates.io` 在部分网络下不可达，需在 `~/.cargo/config.toml` 配置镜像源。
- **3 个新命令已通过实盘验证**：连真实主站（`116.205.183.150:7709`）实测 `0x02cf` 返回 16 条目录、`0x02d0` 返回 1533 字符的平安银行 F10 正文（含当日更新日期）、`0x02c5` 返回 `size=329507` 与 md5，三者均在 0.05 秒内返回。实盘返回的首条目录记录（`最新提示` / `000001.txt` / start=0 / len=23426）与差分 fixture 中按 Rust 解析器推导出的值**逐字段一致**，且 23426 正是 `easy_tdx` 纯 Python 实现取回同一文件的字节数。

### 文档

- 新增 [从 easy_tdx 迁移](MIGRATION_FROM_EASY_TDX.md)：把 `easy_tdx` 1.20.7 → eltdx 的差异按「🔁 改名 / 🎯 有意不同 / ⏳ 尚未提供 / ✅ 已对齐」四类逐项列出，含 14 条离线 API 名称映射（全部实测对照签名）与迁移自查清单。
- [F10_7615.md](F10_7615.md) 增补**实盘验证状态**：`python -m eltdx.f10_smoke --code 000001` 5/5 通过（约 1.1 秒）；并说明 easy_tdx 1.20.7 **没有任何 7615 实现**（全仓检索命中 0 次），故该通路无同协议对比对象。同时记录 7709 文本型 F10（`0x02CF`/`0x02D0`）的可用性取决于原生模块版本：随 `v3.2.3` 发布的 `_native` 不含这 3 个命令（`0x02c5`/`0x02cf`/`0x02d0`）会抛 `UnsupportedCommandError`，而由本仓库源码编译出的 `_native` 已包含它们；`resources.read()` 在任何情况下都无法替代（返回空块）。
- **测试：命令注册表计数 22 → 25**：`7057088` 新增 `block_meta`(0x02c5) / `company_info_category`(0x02cf) / `company_info_content`(0x02d0) 后，`test_command_registry_contains_7709_documents` 与差分矩阵测试仍写着 22。前者已更新并补上 3 个新码断言。
- **~~已知缺口：3 个新命令没有差分 fixture~~ 已补齐**。这 3 个命令的 fixture 原先缺失，因为请求编码与响应解析都在 Rust 侧（`eltdx.protocol` 走 `call_native`），而随 `v3.2.3` 发布的旧 `_native` 会对它们抛 `UnsupportedCommandError: unsupported command: 0x02c5`。从源码重编 `_native` 后已补齐，`PENDING_DIFFERENTIAL_FIXTURES` 清空，`tests/native` 由 97 → 103 passed（详见上面「25 个 7709 命令全部有差分 fixture」）。

## v3.2.3 - 2026-10-05

- 新增 `client.delisted_bars.get()`，查询退市股票的不复权日线，支持自动分页。
- `code` 支持单个字符串、列表或元组；批量返回以标准代码为键的字典，每只股票独立翻页，`batch_size` 控制并发。
- 修复 `max_pages` 参数校验：仅接受正整数或 `None`，无效值在发送请求前报错。
- 修复批量代码校验接受全角等非半角数字的问题，所有代码校验通过后才开始查询。
- 补充退市日线接口参数、返回样本和批量示例，改善参数表在桌面和手机上的显示。

## v3.2.2 - 2026-09-13

- `client.helpers.board_quotes()` 默认查询概念板块，新增 `category` 参数，支持概念、风格、地区、880 行业、一级/二级/三级行业和全部板块。
- 补充板块分类字段、行业编码和各分类输入输出文档。

## v3.2.0 - 2026-09-12

- F10 请求默认优先使用 IPv4，IPv4 连接失败后继续尝试 IPv6；可通过 `prefer_ipv4=False` 恢复系统顺序。连接策略只作用于 F10，不修改全局 DNS，也不串行化并发请求；地址依次尝试，仍使用配置的连接超时。

## v3.1.9 - 2026-09-12

- 修复客户端精度元数据加载时对无前缀 `92xxxx` 代码的市场识别：正确归类为北交所；`900xxx` 仍归类为上海 B 股。

## v3.1.8 - 2026-09-12

- 新增可选的历史成交批量数据入口 `history_batch()` / `all_history_batch()`，支持单代码和代码列表，原有接口签名和返回类型保持不变；成交接口的代码列表能力本身在 `v3.1.7` 已支持。
- 新增 `TradeBatch`，支持按列读取、按索引筛选、按需转换 `TradeTick` / `TradePage`，并支持显式 JSON 导出。
- 池化、单连接和 pin transport 直接复用原始字段块；只实现旧接口的自定义 transport 保持兼容。批量路径不修改 Rust 协议及 ABI。

- 分时 Python 接口及 `eltdx_minute`、`eltdx_trades` MCP 工具新增代码列表，并通过 `batch_size` 控制并发；`eltdx_trades` 对应的 Python 成交接口列表能力不属于本版本新增。
- `TradeBatch` 复用现有 Rust native DTO，本版本未修改 Rust 协议或 ABI。

## v3.2.1 - 2026-09-13

- 新增 `client.helpers.board_quotes()` 和 `client.helpers.board_member_quotes()`：组合 `0x06b9` 板块资料、`0x044d` 当前证券名单和 `0x054c` 批量行情；按 80 个分批，不负责排序，并支持按服务端日期的每日资料缓存与 `refresh=True` 强制刷新。
- 分类行情目录明确区分 `client.quotes.list_by_category()` 底层原始分页接口与 `client.helpers.realtime_rank()` 榜单封装。

## v3.1.7 - 2026-09-07

- 按深交所创业板完整 `30` 号段识别深市创业板股票。
- 修复 `sz302132` 等 `302xxx` 创业板股票被错误归类为 `unknown` 的问题。
- 同步 20% 涨跌幅规则、代码表文档和回归测试。

## v3.1.6 - 2026-09-06

- 按 `0x044d` 代码表的 `decimal` 动态解析股票、ETF 和可转债行情价格。
- 修复可转债快照、旧版行情、分类行情、刷新行情和分时价格放大 100 倍问题。
- 客户端缓存证券精度元数据，推送行情复用同一精度注册表。
- 保持 K 线协议解析不变，并补充动态精度说明。
- 修复 `include_raw` 开关：默认关闭时 `raw_payload` / `record_hex` 为空，显式开启才返回原始内容。

## v3.1.5 - 2026-09-06

- 删除 `LimitBoardLadderRow.ladder_days` 冗余字段，统一使用 `board_level` 表示股票实际板位。
- `consecutive_limit_days` 和原生 `lbts` 访问方式继续对应 `board_level`，避免同一含义出现两个公开字段。
- 完善实时涨停梯队与 F10 涨跌停列表文档，明确数据来源、字段口径、封单方向和接口区别。

## v3.1.4 - 2026-09-05

- 修正涨跌停列表解析：使用 `lbts` 作为单只股票板位，补充 `highest_board_level`、`status`、`reason` 字段。
- 新增 `client.f10.limit_up_down_list()` 与 MCP 工具 `eltdx_limit_up_down_list`，旧连板天梯名称继续兼容。
- 补充市场概况、梯队数量与晋级率统计，日期范围按交易日返回对应统计。

## v3.1.3 - 2026-09-05

- `client.bars.get()` 支持传入代码列表，按连接池并发返回以规范化完整代码为键的结果字典；`batch_size` 可限制并发数。
- 新增 `client.f10.limit_board_ladder()` 和 `eltdx_limit_board_ladder`，通过 `CWServ.cfg_fx_lbtt` 查询指定日期 / 日期范围的逐股连板明细，并可选返回市场概况。
- 补充连板天梯 F10 模型、字段映射、接口目录和包内文档镜像。

## v3.1.2 - 2026-09-05

- 集合竞价当日和历史查询统一使用 35 台专用主站；普通行情、K 线和成交接口继续使用默认 43 台主站。
- 创建标准 `TdxClient` 时并发测速普通 43 台和专用 35 台候选主站，合并重复地址后分别缓存排序结果；首次业务请求不再重复测速。
- 测速只使用临时 TCP 探测连接；普通池、集合竞价池和资金流向池按首次使用建立业务连接并完成握手，后续请求复用连接。
- 补充 `realtime_rank()` 全部服务端排序字段、编号和排序方向说明。

## 修复内容

- 避免集合竞价历史请求因落到普通行情主站而返回空数据。
- MCP 客户端注册表适配构造阶段测速，避免构造客户端时持有注册表锁阻塞其他客户端。
- 集合竞价和资金流向专用池复用同一份 35 台主站排名，关闭客户端时统一释放已创建的连接池。

## v3.1.1 - 2026-09-02

- 资金流向 `0x0ffc` 使用独立主站池，避免与普通行情主站列表混用。
- 协议回归改用仓库内当前 7709 golden fixture，不再下载或对比旧版本 wheel。
- `client.bars.get()` 默认按代码自动识别股票或指数，修复指数 K 线布局解析并补充指数上涨 / 下跌家数。

## v3.1.0 - 2026-09-01

- 新增 `client.money_flow.daily(code)`，接入 7709 `0x0ffc` 日资金流向服务。
- `client.money_flow.daily()` 支持传入代码列表，并按连接池并发返回 `MoneyFlowBatch`。
- 返回主力净额、主买净额及两种口径各自的超大单、大单、中单、小单净额。
- MCP 新增 `eltdx_money_flow`，参数和批量规则与 Python API 保持一致。
- 新增资金流向独立详情页、接口目录条目、命令映射、字段说明和真实返回样本。

## v3.0.9 - 2026-08-30

- 成交明细、历史成交明细和 09:25 正式撮合入口现在支持传入代码列表。
- 列表查询返回以规范化完整代码为键的结果字典；底层仍按单股票请求，并按连接池 Slot 并发调度，超出并发数的代码自动排队。
- 同步 API 参考、方法手册、接口目录、包内文档镜像和批量回归测试。

## v3.0.8 - 2026-08-28

- `client.helpers.daily_price_limits()` 现在必须传入 `trade_date`，按指定 T 日计算涨跌停价。
- 参考价改为取 T 日之前最近一根不复权日线；停牌导致没有 T-1 日线时，继续使用最近实际成交日线，找不到则明确返回 `missing_pre_close`，不再使用实时快照兜底。
- 应用 T 日 `0x000f` 权息事件，并输出 `pre_close_trade_date` 和 `pre_close_source`。
- 更新 2026 年 7 月 6 日起主板 ST/*ST 涨跌幅为 10% 的规则。
- MCP 新增 `eltdx_daily_price_limits`，`trade_date` 为必填参数；同步 MCP 文档和工具契约。

## v3.0.7 - 2026-08-28

- 修复 Python 3.10 下 `/methods` 枚举 `WorkdayService` slots 描述符时抛出 `TypeError` 的问题。
- 同步 README 版本化接口横幅和赞助图位置测试，恢复 Python 3.10-3.14 主分支 CI。

## v3.0.6 - 2026-08-28

- 新增可选的 FastAPI 跨语言网关 `eltdx-http`，通过 HTTP JSON 和 WebSocket RPC 调用公开 API。
- WebSocket 支持桥接原生 `0x0547` 行情增量订阅；普通 RPC 仍然是一问一答，推送频率由 7709 主站决定。
- 默认 `pip install eltdx` 不增加 FastAPI/Uvicorn 依赖，也不会启动额外服务；网关依赖通过 `eltdx[http]` 单独安装。
- 新增网关文档、订阅测试、发行包 smoke 检查，并同步包内文档镜像。

## v3.0.5 - 2026-08-27

- `client.corporate.capital_changes()` 和 `adjustment_factors()` 支持代码列表，默认每批 75 只，可通过 `batch_size=1..200` 调整；主站短响应会自动补拉，批次按连接池并发执行。
- `capital_changes()` 覆盖标签 `1..15` 的广义权息、股本变迁、增发、回购、缩股和权证资料；新增 `CapitalChangeBatch` 和 `AdjustmentFactorBatch`。
- 新增 `client.corporate.adjustment_factors()`，仅使用 `0x000f` 标签 `1` 在本地计算事件级前、后复权仿射系数。
- MCP 新增 `eltdx_capital_changes` 和 `eltdx_adjustment_factors`，与 Python API 的批量参数保持同步；MCP 工具总数为 20 个。
- 修正配股字段映射、标签解析、TCP 拆包和复权事件复合逻辑，并补充多市场和批量回归测试。

## v3.0.4 - 2026-08-22

- 修复 `client.trades.all_today()` 和 `client.trades.all_history()` 的分页展开顺序：主站从 `start=0` 返回最新页时，最终结果现在按时间正序返回。
- 保留服务端原始 `absolute_index`，分页合并不会重新编号，便于定位原始成交记录。
- 增加分页顺序回归测试，覆盖当日和历史成交的多页合并边界。
- 修复 v2.0.5 基线导出器遇到 v3 新增模块、方法、数据类或异常时中断的问题；缺失项现在会显式记录并继续生成对照夹具。
- 同步成交明细方法手册、接口总览和包内文档镜像。

## v3.0.3 - 2026-08-20

- 补充最新 A 股股票、ST 和停牌列表封装。
- 新增每日股本、每日涨跌停价、实时榜单、连板天梯和题材强度排行。
- 新增买卖力道、成交对比的命名入口。
- 短线指标补齐开盘价、昨收、开盘量比、普通流通股本、封单等字段；开盘量比按最近 5 个完整交易日计算。
- 更新 README、接口目录、字段手册和 Helpers 文档，并同步 wheel 内置文档。

## v3.0.2 - 2026-08-17

- 成交明细新增 `actual_trades`，在保留原始 `ticks` 的同时排除非成交的 `status=8` 集合竞价快照；09:25、15:00 和普通盘中成交继续作为真实成交保留。
- 新增 `is_actual_trade`、`is_after_hours_fixed_price` 和 `after_hours_trades`，明确识别 15:05-15:30、`status=5` 的盘后固定价格真实成交。
- 成交明细不再把 `status=8` 的原始数量字段解释为竞价匹配量；完整秒级竞价过程、虚拟匹配量和未匹配量统一以 `client.auctions.series()` 为准。
- 修复显式 `connect()` 握手期间并发 `close()` 时仍切换备用服务器的问题，关闭中断现在会立即停止连接流程，避免无谓的 `CloseTimeout`。
- 21 个 7709 原生接口和 16 个 Helpers 页面新增默认折叠、可复制的真实 JSON 返回样本；F10 原生 Entry 页面不新增样本。

## v3.0.1 - 2026-08-17

- `client.auctions.series(code, date=None)` 现在通过 `0x056a` 同时支持当日和历史集合竞价过程快照，并按主站响应顺序保留全部时间点。
- 删除 `client.trades.auction_today()` 和 `auction_history()`；成交明细仍保留原始混合记录及其分类属性，正式 09:25 撮合入口保持不变。
- `client.helpers.auction_data()` 的历史竞价过程改由 `0x056a` 获取；`0x0fc6` 只负责历史 09:25 正式撮合和前收盘参考价。

## v3.0.0 - 2026-08-16

- Native Engine 改为单 Supervisor、自适应 Tokio runtime；worker 默认按 Slot 数和系统逻辑处理器自动计算并允许手动覆盖，单 worker 使用 current-thread 快速路径，两个以上 worker 使用 multi-thread。
- 默认使用测速排名最快2台7709服务器、每台4条连接；新增 canary 握手、受控分批建连、每服务器连接上限和排名后备服务器补位。
- 新增 Engine 全局 raw/decoded 内存预算和峰值 diagnostics；默认 push 字节上限提高到64 MiB，并增加160 Slot压力与资源归零合同。
- 保持 `TdxClient`、模块化业务 API、公开 dataclass、异常、Helpers、F10、MCP 和 CLI，完整 7709 构包、解析和网络运行核心迁入 Rust。
- 新增无 Tokio/Python 依赖的协议 crate、Supervisor/Slot runtime crate 和私有 PyO3 ABI3 扩展 crate。
- 21 个命令全部使用强类型 Rust request/response；公开 `eltdx.protocol` 继续存在，但只委托无状态 native 入口。
- `SocketTransport` 与 `PooledSocketTransport` 统一使用每 Engine 一个 Rust runtime，并实现有界 FIFO admission、absolute deadline、一次安全重试、pin-local FIFO、低优先级心跳和有界 push。
- 保留 diagnostics 和 `ActorSnapshot` 公开字段名；`actor_alive` 现在映射 Rust Slot task，不再存在 Python Actor 运行核心。
- 增加显式 Python/native ABI 校验，移除纯 Python 7709 fallback；安装版本来自 Cargo/distribution metadata。
- 构建产物改为五个 `cp310-abi3` wheel 和一个 sdist，支持 CPython 3.10-3.14 的首发平台矩阵。
- 新增版本绑定的十轮统一测试、黄金 fixture、故障注入、压力、性能、真实主站和安装证据资产。
- 正式版在五个平台完成 wheel 安装验证后，以同一批文件发布到 PyPI 和 GitHub Release。

## v2.0.5 - 2026-08-14

- `client.helpers.factors(code, anchor_date=...)` 支持把指定日期或此前最近交易日的前复权因子归一为 `1`；不传锚点时保持原有结果。
- `FactorResponse` 新增 `anchor_date`，明确返回因子采用的前复权基准日期；后复权因子不受锚点影响。
- `client.helpers.local_adjusted_kline()` 同步支持前复权锚点，并在返回的 `KlineSeries` 中记录锚点日期。
- 本地复权 K 线明确只支持日 K，避免周线、月线按日因子精确日期匹配时静默产生不正确结果；其他周期继续使用 `client.bars` 服务端复权。
- 本地日 K 复权复用同一次不复权日 K 查询，不再重复请求完整日 K 历史。
- 补充锚点计算、返回字段、示例和周期限制文档。

## v2.0.4 - 2026-08-14

- `client.helpers.auction_data()` 现在按是否传入日期使用明确的数据源：当日使用 `0x056a + 0x0fc5 + 0x054c`，历史只使用 `0x0fc6` 自动分页。
- `AuctionData` 新增 `auction_records`，用于返回历史成交明细中的 `status=8` 集合竞价记录；`series` 继续用于当日 `0x056a` 秒级竞价过程。
- 历史查询从同一份 `0x0fc6` 数据中取得竞价记录、09:25 正式撮合和昨收价格基数，不再使用当前行情补历史数据。
- 开盘价、开盘成交量和开盘成交额只取自 09:25 正式撮合；`0x054c` 当日快照只用于补昨收和计算开盘涨幅。
- 补充聚合接口的参数、返回字段、返回示例和底层数据来源说明。

## v2.0.3 - 2026-08-14

- 修复 `v2.0.2` 版本测试仍断言 `2.0.1`、wheel 冒烟脚本仍断言 17 个 MCP 工具导致 CI 失败的问题。
- `client.helpers.auction_data(include_snapshot=False)` 不再在当前交易日额外请求 09:25 正式撮合。
- `TradePage.has_more` 与空页终止的分页规则保持一致，短页不再被误判为已经结束。
- 更新 README 接口目录横幅和当前版本导航，并修正 Helpers 目录说明数量。

## v2.0.2 - 2026-08-14

- 新增 `client.trades.auction_today()` / `auction_history()`，分别查询当日和历史成交明细中的集合竞价记录。
- 新增 `client.trades.opening_match_today()` / `opening_match_history()`，分别查询当日和历史 09:25 正式撮合。
- 删除原先合并查询的 `client.trades.auction_snapshots()` 和 `client.helpers.auction_0925()` 入口；`client.auctions.series()` 继续用于 `0x056a` 集合竞价过程快照。
- 为拆分后的接口补充独立文档和示例，并整理服务器文件相关文档。

## v2.0.1 - 2026-08-14

- `0x0fc5` 当日成交明细和 `0x0fc6` 历史成交明细现在区分普通成交、`status=8` 集合竞价快照和 09:25 正式撮合，并提供对应筛选属性。
- 09:25 正式撮合拆分为 `client.trades.opening_match_today()` 和 `opening_match_history()`，分别固定使用 `0x0fc5` 与 `0x0fc6`；集合竞价记录拆分为 `auction_today()` 与 `auction_history()`。
- 当日分时、当日成交明细和当日集合竞价明细继续使用 `today()` / `all_today()` / `series()` 公开入口；文档明确“当日”指主站当前保存的交易日。
- 代码表、K 线和成交明细按真实服务端单页上限校验，并按实际返回条数推进分页，直到空页确认结束，避免服务端短页造成漏数。

## v2.0.0 - 2026-08-13

- 移除 `TdxClient` 上全部旧版扁平 `get_*` 兼容入口，统一使用 `codes`、`quotes`、`bars`、`minutes`、`trades`、`auctions`、`corporate`、`resources`、`f10` 和 `helpers` 模块。
- 保留全部 7709 原生协议接口，包括 `0x053e` 的 `client.quotes.legacy()` 和 `0x06b9` 的 `client.resources.read()`。
- 将五档补齐、09:25 快照、除权除息、股本、换手率和本地复权等组合能力归入 `client.helpers`。
- 新增成交明细自动分页和全市场证券分类的模块化入口。
- 更新 MCP、smoke、文档和示例，使仓库内部统一使用 2.0 API。

## v1.3.1 - 2026-08-13

- 修复六位北交所 `92xxxx` 代码被通用上海 `9xxxxx` 规则误判为沪市的问题；上海 B 股 `900xxx` 仍保持沪市识别。
- MCP 自定义行情主站现在会在客户端注册前校验 `host:port`，拒绝缺少端口或端口越界的配置。
- MCP 客户端构造失败时会回滚 pending key 并唤醒同配置等待者，避免后续请求永久等待。

## v1.3.0 - 2026-08-04

- 补全短线指标 21 个字段的中文名称、业务含义、单位和来源/计算口径，并明确自由流通 `Z` 口径、百分比/倍数读法及封单字段的适用条件。
- MCP 服务迁移到 MCP Python SDK 2，修复新版 SDK 安装后无法导入旧 `FastMCP` 的问题。
- MCP 新增五档盘口、分时、成交明细、当日集合竞价、竞价汇总、短线指标、财务报表和公司资讯工具，并发布 8 个内置文档资源。
- MCP 服务现在复用有界的 `TdxClient` 实例，在服务退出时统一关闭；工具参数增加批量数、分页数和超时边界。
- CI 显式安装 MCP optional dependency，并通过 SDK 2 客户端验证工具发现、调用、资源读取和客户端生命周期。
- `0x0547` 增量刷新单次最多接受 100 个代码，避免主站静默截断第 101 个及之后的结果；实时完整五档统一通过 `0x0547` 首次刷新和推送获取。
- MCP 行情客户端按 `host + timeout` 独立初始化，每组使用 4 个连接槽位并支持空闲 LRU 淘汰；同服务器多线程调用不会直接共用同一个 socket，F10 不占用行情客户端槽位，服务退出会等待在途行情调用完成。

## v1.2.0 - 2026-07-19

- 新增 `client.helpers.shortline_indicators()` 和兼容入口 `client.helpers.get_shortline_indicators()`，返回固定 21 个统计资源及短线计算字段。
- 新增 `ShortlineIndicatorTable`、`ShortlineIndicator`、`ShortlineIndicatorsNotReadyError` 和 `TdxStatsDateError`。
- 目标交易日来自 TDX 握手，上一交易日来自上证指数实际日 K；`tdxstat.cfg` 与 `tdxstat2.cfg` 必须日期一致且主导日期覆盖率均不低于 95%。
- 统计资源仅接受目标交易日或上一实际交易日；过期、CFG 日期冲突、低覆盖率及交易日 09:25 前未就绪等情况明确失败，不跨日猜算。
- 已验证统计资源在客户端内存缓存；`refresh_stats=True` 可强制刷新，`client.clear_cache()` 同步清理统计缓存，不新增数据库或磁盘缓存。
- README、Pages 接口目录、API 参考、方法手册、字段手册和短线指标专页同步补充调用及字段口径。

## v1.1.0 - 2026-07-19

- 7709 transport 改为每连接槽位一个单线程非阻塞 `ConnectionActor`。
- 请求使用全池 FIFO admission、exact-once lease 和真正独占的 `pin()` proxy。
- `timeout` 现在覆盖数字 IP/已缓存 endpoint 的排队、连接、握手、发送、响应和一次 retry。
- push queue 改为有界 buffer；溢出会丢弃最旧帧并通过 `PushOverflowError` 明确报告 gap。
- 新增 `max_pending_requests`、`push_queue_size`、`push_queue_bytes`，以及 `PoolBusyError`、`PushOverflowError`、`TransportCloseTimeoutError`。
- `TdxClient`、`TdxClient.from_hosts()`、`PooledSocketTransport` 和 `eltdx-smoke` 的 `pool_size` 默认值统一为 `1`；该参数现在必须是正整数，非法值直接抛出 `ValueError`，不再静默截断或改写。
- 自定义 hostname 的首次 DNS 仍使用标准库阻塞解析，但在 Actor 外执行，不占 slot；该解析无法提供严格取消保证。
- Actor fatal 或 close deadline 到期现在 fail-closed，不会悄悄创建替代线程。
