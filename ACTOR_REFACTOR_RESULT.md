# Actor Transport Refactor Correction Result

This is the permanent recovery and audit record for the eltdx 7709 Actor
transport refactor. It explicitly supersedes the invalid COMPLETE claim at
`994c49b` and all earlier 183-test acceptance evidence. The later `9a60e769`
completion claim was itself reopened on 2026-07-17 after deterministic tests
proved that the Actor thread could still block on Pool, Broker, Proxy and
sibling-Actor locks. The resulting external-lock correction reached
`f5b63bb`, but was reopened again on 2026-07-17 after deterministic tests found
fatal/admission and fatal/push publication windows. The first reviewed
epoch-retirement correction at `a987c16` was itself reopened after the final
review found unresolved Guard selection and no-error deferred-drain edges. The
F09 FINAL at `5925c02` was overturned on 2026-07-19: deterministic tests proved
that standalone normal close could overwrite an Actor fatal, Guard could return
an old-epoch fatal, and the full suite exposed an over-wide heartbeat counter.
The reviewed F10 runtime production source is frozen at
`6abbaf5273aace450972f6e99fe44a8f05307812`; the R5 heartbeat measurement
source is frozen at `f12701f1efed66f70cd267c1c63fbc2d38f96b1d`.
Delivery becomes COMPLETE only after the final `SELF` documentation commit
passes its own exact CI and Pages gates. Source-evidence checks cannot be
substituted for those gates.

## Delivery Identity

| Field | Value |
| --- | --- |
| Status | FINAL manifest; valid only after exact `SELF` CI/Pages and identity checks succeed |
| Authoritative spec | `ACTOR_REFACTOR_PLAN.md`, revision 1.4 |
| Spec SHA256 | `63D9BF2CA2568D1CC71DEDDAA5A16B252676F8625035B9493B93149C5D51562D` |
| Performance authorization spec commit | `5ff6447d2acaa04ab8c406970c2a6b81e8ccd94f` (revision 1.2) |
| Final procedural spec commit | `242e7e5dd19eebd47d5ed7d91e0e295b8f642d64` (revision 1.4) |
| Refactor base | `71089c0a2867a75dc79aa2c340213f4e3845b6e3` |
| Overturned acceptance | `994c49b51f47255bdcd9cdc3308a5a554f37588b` |
| Previous implementation checkpoint | `3287b6a775e6c9fe7a0bcecfe134fc94b6d6634d` |
| Reopened baseline | `9a60e769160c8e146525e7d53fd5fa40dac012b9` |
| Current external-lock correction | `abd58c39aef6f905075788d4482eac43e673ba63` |
| Evidence ledger checkpoint | `eac784b` (`Fix-Checkpoint: L04E2`) |
| Epoch-retirement baseline | `45d8bc80f65eb57ee4ff5fab9a420d80aa705c6a` |
| Epoch-retirement red tests | `d4d6c97` (`Fix-Checkpoint: F07-RED`) |
| Epoch-retirement production checkpoint | `a987c16` (`Fix-Checkpoint: F07`) |
| Epoch-retirement verification checkpoint | `da8854e` (`Fix-Checkpoint: F07E`, push retry recorded) |
| Epoch-retirement CI correction | `bc6990a8b0e6f350ef46ac2884930720fdd5a338` (`Fix-Checkpoint: F07-CI-R1`) |
| Final-review RED tests | `ee077cc` (`Fix-Checkpoint: F08-RED`), `12ea212` (`Fix-Checkpoint: F08-RED2`) |
| Current epoch-retirement production | `3589a09095c21908dd738e266e295393b91548e8` (`Fix-Checkpoint: F08`, historical predecessor) |
| Current F09 RED tests | `19d6d74` (`Fix-Checkpoint: F09-RED`) |
| Current P2 invariant evidence | `f0d9ce7` |
| Current Guard production fix | `45e6703` (`Fix-Checkpoint: F09-FIX`) |
| Current verification checkpoint | `f117871` (`Fix-Checkpoint: F09-TEST`) and `ddce09b` (`Fix-Checkpoint: F09-EVIDENCE`) |
| Stress/performance artifact source | `f1178712bf108d113db7a345f53d3a9e9e0d113b` |
| Overturned F09 FINAL | `5925c02f76a7a905d714900b1e16a907ada2f73f` |
| F10 RED tests | `807d2a553c7f87567d36a4f2e8cc1e490d09121f` (`Fix-Checkpoint: F10-RED`) |
| F10 runtime production source | `6abbaf5273aace450972f6e99fe44a8f05307812` (`Fix-Checkpoint: F10-HEARTBEAT-R4`) |
| Overturned F10 R4 FINAL | `64bbea9bd1965426e30e24f4f10e99d1144a831b` (reopened by exact-final out-of-order heartbeat review) |
| F10 R5 measurement source | `f12701f1efed66f70cd267c1c63fbc2d38f96b1d` (`Fix-Checkpoint: F10-R5-FIX`) |
| F10 R5 clean evidence source | `1dd1dcd79e3bccbec72e01dc50c84bbc850e9d9d` (`Fix-Checkpoint: F10-R5-TEST`) |
| Exact preceding FINAL checkpoint | `ac942a87cd1f1fd78b5486bc29660361c7af380e` (CI `29648788642`, Pages `29648788648`, both SUCCESS; historical) |
| Final manifest commit | `SELF`, resolved by the first-parent FINAL trailer below |
| Final delivery HEAD | `SELF`, the first-parent commit carrying `Fix-Checkpoint: FINAL` |
| Branch | `actor-transport-refactor` |
| Draft PR | [#12](https://github.com/electkismet/eltdx/pull/12), OPEN, draft, unmerged |
| Exact-source CI | Resolved after normal push of final `SELF`; exact run URL and conclusion are in the final delivery report |
| Exact-source Pages | Resolved after normal push of final `SELF`; exact build URL and conclusion are in the final delivery report |

The previous `SELF=9a60e769...` is overturned. `SELF` is the newest
first-parent commit containing this manifest, with no
`ACTOR_REFACTOR_FIX_PROGRESS.md`, and with trailer `Fix-Checkpoint: FINAL`:

```powershell
git log -1 --first-parent --format="%H%x09%B" --grep="Fix-Checkpoint: FINAL"
```

A commit cannot embed its own SHA or the Actions run IDs created only after its
push. At delivery, local HEAD, the remote branch, and PR head must all equal
`SELF`; resolve `SELF` with the first-parent command above. After the exact
`SELF` push, recover the six CI jobs and Pages build with
`gh run list --commit SELF`. Persist those exact URLs and conclusions in the
existing PR #12 delivery comment and in the final report; do not create another
repository commit merely to copy run IDs into this manifest.

## Correction Checkpoints

| Phase | Commits in first-parent order | Result |
| --- | --- | --- |
| Original A00/A01 | `f016868`, `0a1f034`, `79a14f9` | Baseline, remote synchronization, deterministic Actor infrastructure |
| Original A02/A03 | `20387d6`, `608fdeb` | Incremental decoder and nonblocking Actor runtime |
| Original A04/A05 | `949c787`, `5f82000` | Wire lifecycle and SocketTransport facade |
| Original A06/A07 | `e7d8fca`, `049f101` | FIFO pool leases, pin proxies, lifecycle and finalizers |
| Original A08/A09 | `bf6fed2`, `9755ee5`, `c2c4eb0`, `b30c6b9`, `c403681`, `994c49b` | Stress/platform/docs, decoded budgets, heartbeat guard and overturned final evidence |
| Correction F00-F06 | `05a5e9b`, `8aa089d`, `2e48be0`, `117b8c6`, `0955a8e`, `cc46e60` | Baseline ledger through resource-sampling correction |
| Final lifecycle review | `0b8ad54`, `b66a7a8` | Shutdown, startup, finalizer and post-review cleanup gaps |
| FIFO-v1 diagnosis | `dcf6190`, `2058ee6`, `359bb47`, `11be931`, `ca43972`, `8303405` | Hot path, evidence conflict, contract diagnosis, frozen campaign and retained FAIL |
| Post-campaign correctness | `7b961fe`, `a53cc09` | Partial-send receive order, connect cancel, lifecycle interruption and deterministic generation failover |
| FIFO-v2 low-risk cycle | `66e4496`, `72ef660`, `8296511`, `d76ca47`, `2da7651`, `d9619b0` | Campaign freeze, Windows deadline, low-risk hot path, remote checks and retained FAIL |
| Windows/pool experiments | `052ff68`, `76c3a95`, `e106ad4`, `0183c49`, `9338286`, `2d4cea8` | Rejected lock/return candidates, Actor cooperation, pool hot path and evidence |
| Post-hotpath correctness | `3201d3d`, `907e3e6` | Actor/pin race fixes and exact correction checks |
| Revision-7/final campaign | `f7355c0`, `7923287`, `7e78bca` | Heartbeat/DNS evidence, revision-7 checks and immutable FIFO-v2 FAIL |
| Rejected successor candidates | `29b250e`, `f0a329a`, `89d6439`, `792b3db`, `e9d2c8c`, `2a4e396` | Wake, pre-send, snapshot, diagnostic and Broker candidates rejected without favorable resampling |
| Exception/control/final evidence | `eacbfc0`, `e455234`, `5ff6447`, `3287b6a`, `e94f9cd`, `e924d4d` | Exact heavy evidence, blocker audit, revision 1.2 authorization, control priority, exact final-source evidence and revision 1.3 manifest candidate |
| Overturned FINAL | `9a60e76` | Reopened: Actor external-lock blocking remained |
| External-lock correction | `7f8e120`, `8b68542`, `f5ad8a3`, `48b32d6`, `166ae61`, `abd58c3`, `eac784b` | Nonblocking Actor handoff, deferred settlement, bounded FIFO lease pulses, two pin publication corrections, per-call identity cell and exact evidence ledger |
| Superseded epoch-retirement correction | `d6b9296`, `f290981`, `721cbe8` | Earlier deterministic publication-race correction; reopened by the final fatal-reason review |
| Reopened fatal-reason FINAL | `d4d6c97`, `a987c16`, `da8854e`, `24af0dc`, `5bcc768`, `bc6990a`, `96b7b98`, `d38bfc6` | Reopened: final review found an unresolved runtime-fatal fallback, owner reason override, and no-error deferred Push drain |
| Current fatal-reason correction | `ee077cc`, `12ea212`, `3589a09`, `dade830`, `a8402a4` | Deterministic RED edges, resolver owner selection, resolver-only Guard fallback, complete deferred abandon drain, and exact-source heavy verification |
| F09 fatal publication correction | `19d6d74`, `f0d9ce7`, `45e6703`, `f117871`, `ddce09b`, `ee5a995` | Guard stale-None RED/REEN, diagnostics and epoch isolation, standalone Push/handle single-writer evidence, stress/performance/package/docs verification and correction evidence record |
| Overturned F09 FINAL | `5925c02` | Reopened by F10 deterministic Push/Guard races and a clean full-suite heartbeat measurement failure |
| F10 correction | `242e7e5`, `807d2a5`, `6c344d4`, `2aea276`, `043966e`, `bc61e26`, `c5afeb4`, `d3e1153`, `6abbaf5`, `bad414a`, `64bbea9`, `a8cc5b3`, `f12701f`, `1dd1dcd`, `fd2070c`, `ff3b1e0`, `027935a`, `7da60eb`, `4c02ce0`, `45663bf` | Revision 1.4 identity; Push/Guard and heartbeat R1-R4 correction; overturned R4 FINAL; R5 out-of-order RED, phase-wide wire fence, evidence and deterministic send/finish review coverage |
| FINAL manifest | `SELF` | Permanent result plus temporary progress-ledger deletion; exact-SHA CI/Pages resolved after push |

This table covers every commit from the original A00-A09 implementation and
every correction-cycle commit through the F10 evidence source. All were
appended and pushed normally; no published commit was amended, rebased or
force-pushed.

## Correctness Corrections

### Frame and request boundary

- Every received frame has a monotonically increasing receive sequence. Each
  wire exchange captures its receive boundary, and a response must be newer
  than that boundary and fully sent before it can match.
- STOP and exact cancel are drained before work. Decoded frames and the socket
  receive batch are classified before the next wire exchange starts, including
  batches larger than the 64-frame fairness budget and handshake-batch tails.
- Decoder continuation uses one ProtocolError/OSError/EOF boundary. A partial
  response at EOF is a retryable connection close; complete malformed protocol
  data remains a non-retryable ProtocolError.
- Old/future-ID poison frames become bounded push data and cannot complete the
  next request.

### Ticket, cancel, build, and deadline

- Connect and request tickets have exact monotonic request IDs plus runtime and
  lease identity. Late standalone and reused pinned-lease cancellation is a
  no-op unless the exact active/pending ticket matches.
- Wake notification failure atomically withdraws and terminalizes the exact
  pending ticket.
- Unsupported command, invalid market, negative start, and other frame-build
  errors fail only that ticket. The Actor and pool remain usable.
- Ticket waits use the caller's absolute monotonic deadline without fixed
  50ms/100ms grace. Endpoint candidates and one retry share that deadline.

### Control priority and terminal ownership

- Heartbeat admission calls the Broker guard outside the Actor control lock,
  then atomically rechecks STOP, active/pending work, exact cancels, generation,
  interval and activity before publishing an internal ticket.
- Every new TCP generation and every wire send has an exact control-lock claim.
  If STOP or the exact `(runtime_epoch, request_id, lease_id)` cancel wins first,
  no socket creation, retry progression or wire send begins.
- Decoded terminal responses, non-terminal handshake phase transitions,
  ConnectTicket success and all final failure paths linearize on the same
  control lock. `terminal_claimed` gives one completion owner; a later cancel is
  a no-op and cannot leave a stale token.
- Heartbeat and handshake payloads are parsed before terminal success is
  claimed. Malformed input fails its ticket, releases the request owner and
  leaves the Actor usable for a later valid request.

### Endpoint failover and Windows

- Handshake failure, partial send, EOF, partial-frame EOF, response timeout,
  and retry rotate from the failed endpoint to the next endpoint instead of
  resetting to index zero.
- Windows READ/WRITE completion verifies `SO_ERROR` and peer identity. Errno
  sets include platform values such as WSAEINTR without hard-coded platform
  assumptions.
- An anomalous ready socket whose `SO_ERROR` remains in progress is unregistered
  and selector-rearmed at a bounded 10ms probe interval, not busy-polled.
- Real two-loopback tests cover refused first address, handshake EOF, partial
  business response EOF, response failure, healthy backup, and one deadline.

### Broker, pin, and lifecycle

- Every admission has a fresh Event. Reservations are decremented before wake,
  eliminating Event ABA and double-decrement races while preserving FIFO.
- Pinned connect/execute are pin-local admitted operations. Pinned close is a
  monotonic OPEN/CLOSING/FAILED/CLOSED state machine and never releases a slot
  before its exact pending/active wire ticket is terminal.
- Actor candidates are installed before `Thread.start()`. Startup errors retain
  the exact runtime, and startup cleanup remains owned until every stage ends.
- Mailbox submission and pool epoch retirement share a submission gate. The
  runtime guard validates exact broker/epoch identity and seals before stop.
- Concurrent close and FIRST_EXCEPTION rollback share one identity-bound
  `ShutdownAttempt`. Old attempts cannot stop a reopened epoch, failure states
  are monotonic, and all closers observe the same result.
- Actor completion and fatal callbacks now only publish immutable identity
  state with nonblocking try-lock/Event operations. Heartbeat contention skips
  the interval, and Push offer/drop uses Actor-owned publication; all Broker,
  Pool, Proxy and sibling settlement runs on a caller/start/close owner under
  the original absolute deadline.
- Lease release uses one durable pulse and wakes only the first live FIFO
  waiter. Each active pin call is one immutable `_PinActiveCall` containing the
  exact call ID and its terminal Event. Active transition replaces that single
  state reference; stale success, timeout fallback, publish and clear paths can
  only touch their detached old Event and cannot overwrite the new call.
- Every pool epoch now gives Broker and Push the same permanent retirement
  Event; each component also has a permanent local-close Event. Broker lease,
  batch, queued waiter, assignment, pin reservation, reclaim and heartbeat
  publication paths recheck that predicate after their canonical container and
  immutable snapshot change, then drain and reject if retirement won.
- Fatal fanout retires the epoch, publishes Broker/Push close, wakes immutable
  waiter/pin/push snapshots and stops every same-epoch Actor before attempting
  the failure-cell try-lock. The try-lock controls only reason bookkeeping;
  current runtime fatal snapshots remain authoritative if it is contended.
- Push offer checks termination before locking, after locking and after append;
  a losing append is removed. Poll rechecks permanent termination after waiter
  registration and Event clear, and fatal/error is observed before any buffered
  frame. Broker and Push close always retry their idempotent drain.

## Compatibility and Scope

Preserved public behavior:

- `TdxClient`, `SocketTransport`, `PooledSocketTransport`, context managers,
  all existing 7709 business methods, automatic handshake, push APIs,
  `connected_host`, `last_handshake`, `last_heartbeat`, and diagnostics.
- `pool_size=N` still creates exactly N Actor slots/connections, independent of
  the host count. No process-global worker pool or per-host thread expansion was
  introduced.
- Caller-side business parsing remains outside the Actor and releases a normal
  lease at wire terminal.

No 7615 source, business command API, `main`, tag, release, PyPI state, or
unrelated Pages content changed. Runtime dependencies remain empty.

Intentional compatible extensions remain bounded defaults:

| Parameter | Default |
| --- | ---: |
| `max_pending_requests` | `256` |
| `push_queue_size` | `1024` |
| `push_queue_bytes` | `8,388,608` |

## Capacity Evidence

| Structure | Observed maximum | Configured hard limit | Evidence |
| --- | ---: | ---: | --- |
| Actor business mailbox | 1 active wire ticket | 1 | deterministic control-priority and submission-gate regressions reject a second active exchange |
| Pool admission | 3 FIFO waiters | 4 in the deterministic test; 256 by default and in heavy stress | `test_lease_broker_assigns_waiters_fifo_and_releases_exactly_once` observes waiter depths 1, 2 and 3 in order, then zero |
| Active normal leases | 4 | `pool_size=4` | 100,000-request heavy workload records server maximum active exactly 4 and zero leases after close |
| Push frames | 1,024 | 1,024 | retained exact-`abd58c3` stress records `max_frames_observed=1024` and zero after close |
| Push wire bytes | 28,612 | 8,388,608 | retained exact-`abd58c3` stress records `max_bytes_observed=28612` and zero after close |
| Incremental RX bytes | at most 32 | 32 in the bounded regression; 65,551 in production | 1,000-byte garbage feed asserts `max_buffer_observed <= 32` |
| Resynchronization discard | exactly 1,000 | 1,000 in the bounded regression; 65,536 in production | the same feed reaches the configured discard boundary without retaining unbounded input |
| Decoded-frame queue | 910 appended; 846 retained after the immediate 64-frame fairness slice | 1,024 | the 1,101-frame legal burst uses 18-byte frames and a 16,384-byte capped recv; an exact-source tracking probe observed 910/846 and the regression drains through the matching response without loss |
| Frame/decompressed payload | 65,535 bytes | 65,535 bytes | declared, compressed, output and trailing-data boundary tests pass |

All final snapshots have zero pending/active tickets, cancel tokens, admission
waiters, pin waiters and leases. Push frames and bytes are zero after close.

## Deterministic Regression Evidence

The original A-E corrections were made red against `994c49b` before their
corresponding fixes. They cover stale decoded and handshake-batch frames,
greater-than-64 continuation, EOF and partial EOF, colliding IDs, late cancel,
request-local build errors, absolute deadlines, multi-endpoint rotation,
Windows refused-first connect, Event ABA, pin close/capacity, fatal late
registration, concurrent start/close and monotonic failed shutdown.

Post-campaign review added deterministic red tests for partial-send receive
ordering, cancellation while connecting, interruption cleanup, generation
failover, Broker reclaim and lifecycle publication. Post-authorization review
then made the following old direct paths fail deterministically before
`3287b6a`: heartbeat admission after a business/control winner, new generation
start after cancel/STOP, decoded terminal response after cancel/STOP,
handshake-phase advance after cancel/STOP, ConnectTicket success after
cancel/STOP, deadline/build/final failure after the winning control and stale
cancel after terminal claim.

The 2026-07-17 external-lock correction was first red at exact `9a60e769`:
the focused selection produced 6 failures/1 pass while guard, Broker, Push and
sibling locks kept failed Actors alive and Lease/Pin completion blocked. Final
review then found the pin publication clear race at exact `f5ad8a3`; its four
controlled scenarios produced 2 failures/2 passes before `48b32d6`.
The next exact-source review found that an old settler's second condition
acquisition timeout could republish call 1 over already-published call 2 at
`166ae61`. Two behavior-only tests applied to that source failed because the
next owner left `_active_call == 2`; `_PinActiveCall` in `abd58c3` closes both
the timeout-fallback and direct stale-publish paths.

Three parameters are retained as intermediate-fix regressions rather than
misrepresented as old-HEAD failures: malformed heartbeat, request-retry plus
cancel, and request-final plus cancel already passed at `5ff6447`. They protect
the final terminal-claim ordering introduced later.

Permanent reproduction-to-fix mapping (all nodes are deterministic):

| Area | Regression nodes |
| --- | --- |
| A: receive/request boundary | `tests/test_transport_actor_regressions.py::test_old_decoded_batch_cannot_complete_next_request_after_64_frame_budget`; `::test_handshake_batch_tail_cannot_complete_business_exchange`; `::test_decoded_backlog_then_eof_reconnects_instead_of_failing_actor`; `::test_response_requires_new_receive_identity_and_complete_send`; `::test_legal_push_burst_above_decoded_queue_limit_keeps_response_live` |
| B: request identity, cancel, build isolation | `tests/test_transport_actor_regressions.py::test_late_cancel_of_completed_ticket_does_not_cancel_next_lease_zero_request`; `::test_cancel_request_during_connect_drops_generation_before_terminal`; `::test_ready_actor_survives_request_build_errors`; `tests/test_transport_pool_regressions.py::test_late_cancel_on_reused_pinned_lease_is_noop`; `::test_invalid_payload_releases_normal_and_pinned_capacity` |
| C: endpoint rotation and Windows connect | `tests/test_transport_failover_regressions.py::test_handshake_eof_retry_starts_next_real_loopback_host`; `::test_business_eof_retry_starts_next_real_loopback_host`; `::test_partial_business_response_eof_retries_next_real_loopback_host`; `::test_response_attempt_timeout_retries_next_host_within_absolute_deadline`; `::test_all_failed_hosts_share_one_absolute_deadline`; `::test_windows_closed_first_endpoint_reaches_healthy_before_shared_deadline` |
| D: Broker, pin, capacity | `tests/test_transport_pool_regressions.py::test_admission_waiter_late_set_cannot_wake_next_acquire`; `::test_pinned_close_timeout_can_finish_cleanup_and_restore_capacity`; `::test_concurrent_pin_close_shares_control_lock_timeout`; `::test_pinned_connect_is_an_active_operation_for_close`; `::test_pin_close_before_first_wire_submission_rejects_operation`; `tests/test_transport_pool.py::test_lease_broker_assigns_waiters_fifo_and_releases_exactly_once` |
| E: Actor/pool lifecycle | `tests/test_transport_lifecycle_regressions.py::test_runtime_registered_after_pool_fatal_is_stopped_immediately`; `::test_close_cannot_return_while_unpublished_candidate_is_alive`; `::test_concurrent_pool_close_cannot_overwrite_failed_closing`; `::test_pool_connect_stops_real_candidate_blocked_during_startup`; `::test_fatal_during_pool_join_cannot_be_published_as_stopped`; `::test_guard_abandon_cannot_miss_runtime_appended_after_snapshot` |
| Post-authorization control/terminal ownership | `tests/test_transport_actor_regressions.py::test_business_submission_wins_heartbeat_admission_race`; `::test_control_change_wins_heartbeat_admission_race`; `::test_control_winner_prevents_new_generation_connect`; `::test_control_winner_prevents_decoded_response_success`; `::test_control_winner_prevents_handshake_phase_advance`; `::test_control_winner_prevents_connect_ticket_success`; `::test_control_winner_prevents_terminal_failure`; `::test_late_cancel_after_terminal_claim_is_noop_without_token` |
| External-lock and deferred publication | `tests/test_transport_lifecycle_regressions.py::test_failed_actor_exits_without_waiting_for_pool_owned_locks`; `tests/test_transport_pool_regressions.py::test_lease_completion_returns_without_waiting_for_broker_condition`; `::test_pin_completion_returns_before_proxy_condition_and_lazily_advances_fifo`; `::test_heartbeat_skips_broker_contention_and_actor_still_processes_stop`; `tests/test_transport_actor_regressions.py::test_terminal_completion_publishes_while_request_gate_condition_is_held`; `tests/test_transport_lifecycle_regressions.py::test_actor_stop_does_not_wait_for_owned_push_condition`; `tests/test_transport_pool_regressions.py::test_pin_old_terminal_settler_preserves_new_publication_before_return`; `::test_pin_old_terminal_clear_rechecks_concurrent_new_publication`; `::test_pin_exact_old_terminal_publication_clears_without_replay`; `::test_pin_stale_terminal_timeout_cannot_overwrite_newer_publication`; `::test_pin_stale_terminal_publish_cannot_replace_newer_publication` |

Historical local commands on production source `3287b6a`:

| Command | Result |
| --- | --- |
| Control-priority focused selection | 11 passed, 100 deselected in 0.51s |
| `tests/test_transport_actor_regressions.py` | 111 passed in 3.56s |
| `python -m pytest -q` | 547 passed in 250.14s |
| Heartbeat hard-gate node | PASS in 209.30s |
| `python -m build` | sdist and wheel built successfully |
| `python -m mkdocs build --strict` | PASS in 3.64s |
| `python -m compileall -q src tests scripts` | PASS |

Package SHA256 values are
`04F3457FF0032E244A50728D1BEE42B9AC5B9E4A131BF471C004E12A1CCBE9A5`
for the sdist and
`0709D124B9055BC2AEBDFFB8F067DA16C522C03666F5F0866460AD19FED960A6`
for the wheel.

Historical frozen local evidence on clean source `abd58c3` (superseded by the current delivery evidence below):

| Command | Result |
| --- | --- |
| Eight pin publication/deadline tests, 20 independent processes | each 8 passed |
| `tests/test_transport_pool_regressions.py` | 85 passed in 1.92s |
| `tests/test_transport_lifecycle_regressions.py` | 92 passed in 7.82s |
| Actor/Pool core selection | 156 passed in 4.13s |
| `python -m pytest -q` | 598 passed in 268.96s; source/test hashes unchanged |
| `python -m build` plus `twine check` | wheel and sdist PASS |
| `python -m mkdocs build --strict` | PASS in 2.70s |

The frozen SHA256 values for `src/eltdx/transport/pool.py` and
`tests/test_transport_pool_regressions.py` are respectively
`4AE60312C9BD979E9D1B4204398BDCDF761E1E1A09D857804061D73A76DD2C96`
and `A456103653C11A40104559792DA956929A1807A552091A0A860A67B84D776AAD`.
The exact package artifacts are retained outside the worktree under
`artifacts/dist-abd58c3`: wheel 307,784 bytes, SHA256
`B7C332788F3AAC8767A936C627E79173C108141AC12C68C7ACEAC1D5B2A4E61B`;
sdist 365,290 bytes, SHA256
`03A67D00280E690CB7D19E3561C72DAC62FC8A5E7882EE3EA5195ED42BE19FB4`.

## Historical Stress, Ownership, and Resources

The retained raw artifact is
`<external-artifacts>/actor-lock-l03rr2-stress-abd58c3.json`,
736,900 bytes, SHA256
`CB82B74C2C69A674144DE9B8D120690E830475E6A144EAAA219FB255337C2FF2`.
It records exact clean source `abd58c3`, workload SHA256
`f7e187e3960002fbf0194c686182c3676152eba7c6fd68ab4bc46ede8262e5b1`,
Windows 11 and Python 3.12.6.

Workload hashes cover raw checkout bytes. The detached Windows evidence
worktree used CRLF, producing `f7e187e...` for stress and `4ddd761f...` for the
benchmark; the LF Git blobs/primary checkout produce `487b3131...` and
`b09ab713...`. No comparison mixes those byte variants.

| Workload | Raw result |
| --- | --- |
| 10,000 generations | 26.620140s, 375.655 rps, one Runtime/Actor/thread identity, two real loopback servers, accepts 5,000/5,000 |
| Generation ownership | 15,000 attempts, 5,000 cross-endpoint retries, 10,000 unique; duplicate/missing/unexpected/stale/cross-request/cross-generation all 0 |
| 100,000 mixed, pool 4/concurrency 100 | 113.677247s, 879.684 rps, 100,035 attempts, 35 real cross-endpoint retries, server maximum active exactly 4 |
| Mixed ownership | Two servers carried 17,630/82,405 requests; 100,000 unique; duplicate/missing/unexpected/cross-request/cross-generation all 0 |
| Push pressure | 2,043 sent, 1,019 bounded oldest drops, explicit gap, maximum 1,024 frames/28,612 bytes |
| Idle CPU | process CPU ratio 0 |

After both workloads every retained runtime reports Actor dead, STOPPED state,
generation/selector/wakeup/tickets absent, saved TCP/wakeup resources closed,
and cancel map empty. Broker admission waiters, pin waiters and leases are zero
and closed; PushBuffer frames/bytes are zero and closed. Actor threads after
both workloads are zero.

Close latency over 100 samples per condition:

| Condition | p50 ms | p95 ms | p99 ms | Max ms |
| --- | ---: | ---: | ---: | ---: |
| Idle | 3.0437 | 3.5406 | 3.7547 | 3.8377 |
| Loaded | 2.6444 | 3.4256 | 3.8377 | 3.9590 |

All 400 loaded futures terminalized with the expected
`ConnectionClosedError`; every ticket and retained Actor resource was terminal
or closed. Maximum caller-side settlement was 0.5661ms.

Windows resources used three warmup rounds followed by eight measured
50-generation rounds. The measured process-handle values were exactly:

```text
202, 202, 202, 202, 202, 202, 202, 202
```

Every warmup and measured sample also had zero Actor threads, exact owned-
resource cleanup and zero cross-request/cross-generation completions. There is
no tolerance, no monotonic growth and no unexplained allowance.

## Superseded Historical Stress Evidence

Historical exact-`3287b6a` command:

```powershell
python scripts/stress_actor_transport.py --generations 10000 --requests 100000 --pool-size 4 --concurrency 100 --close-samples 100 --heartbeat-requests 1000 --idle-seconds 0.5 --resource-rounds 8 --resource-warmup 3 --resource-generations 50 --output artifacts/actor_stress_final_3287b6a.json
```

The Windows 11 / Python 3.12.6 process was recorded as passing in 185.4s. Its
raw JSON was later deleted and is absent from Git and the external artifact
store. The previously reported artifact/workload SHA256 values are therefore
withdrawn as independently reproducible evidence. The values below are
historical run output only and do not prove the current correction. The run
recorded exact implementation
`3287b6a775e6c9fe7a0bcecfe134fc94b6d6634d` and
`worktree_dirty=false`.

Every logical request uses the existing retry-safe file-content command with a
unique uint32 nonce. The server echoes that nonce, real server ID, connection
ID, and wire-attempt sequence. Two real listeners share the provenance ledger
and inject future-ID poison frames, partial EOF, reconnects, push, and delay.

| Workload | Raw result |
| --- | --- |
| 10,000 generations | 24.813711s, 403.003 rps, exact Runtime/Actor/Thread identity unchanged, accepts 5,000/5,000 |
| Generation ownership | 15,000 attempts, 5,000 cross-endpoint retries, 10,000 unique; duplicate/missing/unexpected/cross-request/cross-generation/stale all 0 |
| 100,000 mixed | 93.119775s, 1,073.886 rps, 100,043 attempts, 43 real cross-endpoint retries, server traffic 21,500/78,543 |
| Mixed concurrency | Server maximum active exactly 4; accepts 43/82 and Actor generations 32/23/38/32 both total 125 |
| Mixed ownership | 100,000 unique; duplicate/missing/unexpected/cross-request/cross-generation all 0 |
| Push pressure | 2,044 push/poison frames, 1,020 bounded oldest drops, one explicit gap |
| Idle CPU | 0.502232s wall, 0 process CPU, ratio 0 |

After close, every retained runtime reports Actor dead, generation/selector/
wakeup/tickets absent, saved TCP/wakeup sockets closed, cancel map empty, and
state STOPPED. Broker waiters, pin waiters, and leases are zero and closed;
PushBuffer frames/bytes are zero and closed. Actor threads after both workloads
are zero.

After three identical warmup rounds, eight complete 50-generation rounds each
measured exactly 201 Windows handles after the workload returned and GC
completed:

```text
201, 201, 201, 201, 201, 201, 201, 201
```

Every round also had zero Actor threads, exact owned-resource cleanup, and zero
cross-request/cross-generation completion. There is no tolerance and no
monotonic growth.

Close latency over 100 samples per condition:

| Condition | p50 ms | p95 ms | p99 ms | Max ms | Gate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Idle | 3.0985 | 3.9851 | 5.7324 | 8.3010 | p99 < 100 |
| Loaded | 2.4216 | 2.9370 | 4.6375 | 4.8599 | p99 < 250 |

All 400 loaded futures terminalized with the expected close error, every
ticket was terminal, and all 800 retained Actor-owned resource snapshots were
closed. Broker waiters, pin waiters and leases were zero; PushBuffer frames and
bytes were zero and closed. The raw file is no longer retained, so that earlier
audit cannot be replayed from the current workspace.

## Historical Heartbeat Evidence

The exact-`abd58c3` retained stress artifact contains the balanced heartbeat
campaign. It ran 4 blocks/32 phases, 260 all-slot configuration barriers, four
idle-connection heartbeat probes and 32 paced heartbeat requests. No heartbeat
entered a business interval.

| Metric | Result |
| --- | ---: |
| Without heartbeat | 586.260 rps |
| With heartbeat | 582.241 rps |
| Aggregate ratio | 0.995261 |
| Absolute impact | 0.4739%, below 1% |
| Block ratios | 1.003429 / 0.987833 / 0.983311 / 1.006579 |
| Median block ratio | 0.995631 |
| Business responses | 35,232 unique |
| Duplicate/missing/unexpected/cross-request/cross-generation | 0 |

## Superseded Historical Heartbeat Evidence

The revision-7 heartbeat JSON is no longer present in Git or the external
artifact store. Its previously reported SHA256 is withdrawn as retained
artifact evidence. The following values are historical output from dirty
implementation `907e3e69...`, not current independently replayable evidence.
It retains all 32 balanced phases, 260 configuration barriers and 131,232
unique business responses. Timed heartbeat was `0/0`, duplicate/missing/
unexpected/cross-request/cross-generation and generation/accept fence
mismatches were all zero. Aggregate enabled/baseline throughput ratio was
**0.998163**, impact 0.1837%, below the strict 1% limit.

The deleted clean `3287b6a` heavy JSON historically reported ratio **0.998884**,
impact 0.1116%, with block ratios
`0.998003/1.004117/1.020108/0.974237`, median block ratio `1.001060`,
35,232 unique responses and all error/cross counters zero. It proves four idle
connection heartbeats and 32 paced heartbeats, with
`heartbeat_during_business=0` and idle CPU ratio zero.

One earlier local full-suite sample measured `0.989062` and failed the strict
`>0.99` node; it is retained as a failed sample, not reclassified. The node was
rerun in isolation and passed in 209.30s, then the stable final local suite and
exact CI matrix passed. Neither deleted JSON is current evidence; the retained
exact-`abd58c3` artifact above supersedes both.

## Historical Performance Evidence

The authoritative frozen campaign is `fifo-v2-7923287-a`, comparing clean base
`71089c0a2867a75dc79aa2c340213f4e3845b6e3` with clean Actor source
`79232870c337a94e5d79eca723d8bf5d09371e89`. It ran all eight predeclared
attempt-1 cells once in fixed
`baseline/current/current/baseline/current/baseline/baseline/current` order.
No result was discarded, replaced or resampled.

| Evidence | SHA256 |
| --- | --- |
| Canonical declaration | `5ab6e75cd12d71e396c09ee592a174b7c4900be69ce606b02527e609428a6cde` |
| Declaration file | `36ff99846b8a300f738b85abc20680686a462e07f4b79161779cf44ff9dbd484` |
| Immutable bundle | `2497cf1e3efe07e449511935661da249238b4443d2a9bae906bebe0ed8373961` |
| Stored report | `954192977dee7699dfd1c8991e0dcf2694fa8a3047ab0174fb93849083ead4d1` |
| Independent replay | `15339fd279e6330672553a7aa53d18498de6666213ddbd0dfa2549505d328b7f` |

The immutable canonical campaign directory is intentionally retained outside
the Git worktree at
`<external-artifacts>/fifo-v2-7923287-a`: 11 files totaling
100,391,782 bytes. Its declaration, eight ordered raw trials, bundle and report
hashes match the table above; the independent replay is retained alongside the
directory and matches its listed hash. This is deliberate evidence, not an
in-repository build output.

Across 32 cases, all 1,000,000 requests, successes, server requests, wire
attempts, unique responses, completion rows and raw latency rows matched
exactly. Duplicate, missing, unexpected, cross-request, cross-generation,
digest and provenance mismatches were zero. Current fixed cohorts completed
10,640 clean boundary checks. Artifact audit and verifier replay were CLEAN,
with `errors=[]`.

The immutable verifier result is **FAIL**:

| Gate | Baseline | Actor | Result |
| --- | ---: | ---: | --- |
| Sequential throughput | 174.410898 rps | 163.773610 rps | ratio `0.939010`, below 0.95 |
| Saturated throughput | 687.407879 rps | 634.593945 rps | ratio `0.923169`, below 0.95 |
| Sequential p50 | 5.6370ms | 6.0193ms | delta 0.3823ms, allowance 0.5637ms, PASS |
| Sequential p99 | 6.1812ms | 6.8017ms | delta 0.6205ms, allowance 0.61812ms, FAIL by 0.00238ms |
| No-backlog p50 | 6.0721ms | 6.6680ms | delta 0.5959ms, allowance 0.60721ms, PASS |
| No-backlog p99 | 6.8170ms | 8.4244ms | delta 1.6074ms, allowance 0.6817ms, FAIL by 0.9257ms |

Saturated raw p50/p99 was baseline `132.56405/536.1256ms` versus Actor
`155.13345/170.9080ms`. The report-only contended-wave p50/p99 was baseline
`78.0597/150.6717ms` versus Actor `89.90885/168.4938ms`. These diagnostics do
not offset any failed gate.

On 2026-07-17 the user selected the preserve-ownership option: keep
Actor-exclusive socket ownership, strict FIFO, synchronous APIs and exactly
`pool_size=N` Actors/connections, with no caller-side direct send. Plan
revision 1.2 authorizes the four disclosed old-implementation comparison
failures as a one-delivery architecture exception. The campaign, thresholds,
raw values and FAIL verdict are unchanged; the exception changes only FINAL
completion policy. Concurrency=N, heartbeat, close, idle CPU, uniqueness, cross
counters and resource cleanup remain hard gates with no exception.

This campaign will not be rerun or reclassified. Future performance-sensitive
changes use the FINAL Actor source as a prospective baseline under a rule frozen
before sampling; this exception cannot hide a future regression.

### External-lock correction supplemental A/B

The correction used exact clean `9a60e769` as its prospective baseline and
exact clean `abd58c3` as current, with fixed order
baseline/current/current/baseline and identical benchmark workload SHA256
`4ddd761fa94e4bb21fd32720dc2afd454a982ebcf69ae4e7579fc93c401e6dac`.

These four files use schema 2, not the frozen schema-4 campaign format. The
formal verifier rejects them for different bundle keys/schema-kind and missing
declaration. They are supplemental correction-regression evidence only and do
not replace, override or reclassify the retained formal FAIL above.

| Artifact | SHA256 |
| --- | --- |
| `actor-lock-l03rr2-baseline-a-9a60e769.json` | `2FDA8EF86ED6AD5E7D453F309EC7876B5BF353CA0922D6743CE851AD80D65FBA` |
| `actor-lock-l03rr2-current-a-abd58c3.json` | `D0241896090436737E86CF95911BFD92602BA398EFD01FB8A7E289E8E21E60E9` |
| `actor-lock-l03rr2-current-b-abd58c3.json` | `3981CDC5EB139BC36EF0998334A9D91BFC6B3460AA6CBABB6E6245E7009CB855` |
| `actor-lock-l03rr2-baseline-b-9a60e769.json` | `B23BE4236BC7737A0BA46EDA45C96D2E9BA2B883FE9122171B8D39A6971FE030` |

All 180,000 requests, successes, server requests, attempts, unique responses
and completion rows reconcile. Error, duplicate, missing, unexpected,
cross-request and cross-generation counters are zero.

Two-run aggregate throughput ratios for pool sizes 1/2/4 at concurrency
1/10/100 are respectively:

```text
pool 1: 0.991165 / 0.983273 / 0.985794
pool 2: 0.992611 / 0.986221 / 0.977728
pool 4: 0.997512 / 0.986695 / 0.995357
```

The pooled range is 0.977728-0.997512; every paired single-run ratio is at least
0.975810. All are above 95%. Schema 2 has no raw latency arrays, so quantiles
are not pooled or averaged: all 18 A-to-A/B-to-B p50 and p99 comparisons pass
`max(10%, 0.2ms)` individually.

| Required case | Baseline | Current | Result |
| --- | ---: | ---: | ---: |
| Pool 1/concurrency 1 pooled throughput | 157.566395 rps | 156.174306 rps | ratio 0.991165 |
| Sequential A p50/p99 | 6.2506/7.3206ms | 6.3587/7.4485ms | PASS |
| Sequential B p50/p99 | 6.3095/7.4481ms | 6.3426/7.4400ms | PASS |
| Pool 4/concurrency 100 pooled throughput | 606.633761 rps | 603.816859 rps | ratio 0.995357 |
| Saturated A p50/p99 | 160.5746/174.8197ms | 163.5688/180.4784ms | PASS |
| Saturated B p50/p99 | 163.6486/175.8370ms | 162.8599/174.8672ms | PASS |

The earlier quick A/B pair is retained with `invalid-` prefixes because its
baseline/current workload hashes differed. A later `l03rr` attempt is also
retained with `invalid-concurrent-` prefixes because an unapproved review
stress process overlapped sampling; the entire uncontaminated `l03rr2` schedule
above was rerun from trial zero. The valid pre-fix diagnostic
`9a60e769` versus `8b685420` found concurrency-100 ratios 0.611/0.537/0.365;
it led to the durable first-live lease pulse and publication-idempotency fix,
but is not FINAL performance evidence.

### Superseded epoch-retirement correction evidence

Exact production source `721cbe8885876364a0e1d42f9802ccf7de51029c`
has the following isolated local evidence on Windows 11 / CPython 3.12.6:

| Evidence | Result |
| --- | --- |
| Deterministic retirement regressions | 30 passed; 20 independent processes each passed all 30 |
| Focused external-lock/fatal selection | 12 passed in 0.28s |
| Complete transport matrix | 410 passed in 15.94s |
| Complete pytest | 628 passed in 255.77s |
| Heavy stress/resource campaign | PASS from exact clean detached source |
| Package and documentation | Rebuilt from the final documentation commit before delivery |

The retained stress artifact is
`<external-artifacts>/actor-retirement-r06-stress-721cbe8.json`,
SHA256 `46122307BD0EC52D2026A1FFB580721546331EFF12618D1E065F9DB2F05EF652`.
It records 10,000 generation changes in 22.089949s and 100,000 mixed requests
at pool 4/concurrency 100 in 96.992518s. Both workloads have exact unique
response counts and zero duplicate, missing, unexpected, cross-request or
cross-generation completions. Mixed maximum business concurrency is exactly
4; after close Broker leases and Push frames/bytes are zero, every retained
Actor-owned resource is closed, all 100 idle plus 100 loaded close samples are
terminal/clean, and eight measured Windows resource counts are exactly 201.

The prospective performance directory is
`<external-artifacts>/retirement-perf-721cbe8-b`: 24 files,
176,164,179 bytes. Its retained canonical `manifest.sha256` contains 23 sorted
`name:lowercase_sha256\n` records and has SHA256
`A5BE46272293B2228A75C0631E21DC0BB6DA57F83976A7BF532FE3246D33B902`.
It compares clean detached `f5b63bb` and `721cbe8` roots with identical
workload SHA256 `4ddd761f...`, using seven declared adjacent A/B pairs in a
balanced 14-trial order. All attempt-1 trials ran once without overlap or
replacement; the existing schema-4 case validator recomputed all 1,750,000 raw
latency rows and completion records with `errors=[]`.

The preceding `retirement-perf-721cbe8-a` directory is explicitly invalid and
excluded: a parent execution interruption left it at 13/14 trials, so its
frozen no-retry rule prohibited filling the missing cell. Campaign B was
declared separately and rerun from trial zero with unchanged policy.

| Frozen prospective gate | Result |
| --- | ---: |
| Sequential throughput median paired ratio >= 0.98 | 0.992309, PASS |
| Saturated throughput median paired ratio >= 0.98 | 0.995063, PASS |
| Saturated p50/p99 role-median ratio <= 1.05 | 1.003311 / 1.008325, PASS |
| No-backlog p99 delta <= max(1ms, 10%) | -0.1479ms <= 1.0000ms, PASS |

The historical Actor-vs-legacy formal campaign above remains **FAIL, user-approved exception**.
This prospective correction result
does not reclassify it. No thread, runtime dependency, background cleanup
worker, unbounded queue or per-request publication object was added; the new
assigned-waiter and fatal-handle snapshots remain bounded by the configured
pool/request ownership for the current epoch.

## F09 Current Delivery Evidence

The F09 production source is `45e6703` and the clean evidence source used by
the stress/performance reruns is `f1178712bf108d113db7a345f53d3a9e9e0d113b`.
The final documentation commit is delivery `SELF`; it changes no production
source. The temporary ledger records recovery until that finalization commit,
after which this manifest plus Git history is authoritative.

| Gate | Result | Artifact / identity |
| --- | --- | --- |
| F09 RED proof | 3 new race tests fail on old code: stale-None returns `None`, diagnostics returns `RUNNING`, slow epoch path returns `None` | `19d6d74`; command: `python -m pytest -q tests/test_transport_retirement_regressions.py::test_guard_failure_linearizes_after_none_snapshot_when_fatal_publishes tests/test_transport_lifecycle_regressions.py::test_diagnostics_does_not_report_running_after_fatal_publication tests/test_transport_retirement_regressions.py::test_guard_failure_slow_path_rechecks_new_epoch_and_ignores_old_reason` |
| F09 targeted RED/REEN | 5 focused tests plus P2 call-graph tests PASS; targeted transport suites `231 passed in 9.56s` | `45e6703`; Guard -> resolver and Push condition -> resolver lock order preserved |
| New race tests, 20 independent processes | 60/60 test cases PASS; `failed=0` | `<repository-root>/artifacts\actor-f09-20proc-45e6703.log`, SHA256 `49400E70509F823A86DE2B5186F573733676E9F4F63574223E39E85CB2B08F62` |
| Complete pytest | `646 passed in 245.37s (0:04:05)` on Windows Python 3.12.6; no xfail or flaky retry | command: `python -m pytest -q` |
| 10k generations / 100k requests stress | PASS; unique 10,000/100,000; duplicate/missing/unexpected/cross-request/cross-generation all 0; max active 4; leases/waiters/pins/frames/bytes/Actor threads 0; resources `190,190,190,190,190,190,190,190`, plateau=true | `<repository-root>/artifacts\actor-stress-f09-f117871.json`, SHA256 `F3A574D9E1DDEEC690C24CDB967AE732863243D2FCDCDC02268B034EF78CAECD` |
| Paired performance campaign | **FAIL, user-approved exception**; exact 8-cell ABBA+BAAB, no integrity errors/retries; sequential ratio `0.918421`, saturated ratio `0.926675`; no new exception added | `<repository-root>/artifacts\perf-f09-f117871\campaign_bundle.json`; bundle SHA256 `043D6306C303481E8AB2052AFCF180CB3BD32EBC3DC5DD9D26F68C83963EEB87`; `manifest.sha256` SHA256 `9942EB0AC0BF8F2AE65A9CD1224DAAB08C8DACD5B481D2C0708B36D66422521A`; declaration SHA256 `7ec426845f5dd3c73d69c781ac11c49836955e333507128a19d973ef5fe540e5`; verifier report SHA256 `4DCFF1CF6C5A6AABA07E256492138EFEECFAC5679C8BA9BA33C5EC2B7E85951B` |
| Package artifacts | PASS; `python -m build` and `python -m twine check dist/*` | wheel SHA256 `CA693A5C9D280341120102DBF7276031E1C908219E407894670320D99C7A16E7`; sdist SHA256 `41D39944B00BF135BC02C7A3604A5B108C7B822DCB7A3BD12829D9AAFA7ED67F` |
| MkDocs strict | PASS; 126 files, 5,685,815 bytes | command: `python -m mkdocs build --strict`, local `site/` artifact |

The historical Actor-vs-legacy performance exception remains exactly
**FAIL, user-approved exception**. The F09 campaign does not reclassify that
exception as PASS and does not introduce another exception. The performance
producer workload SHA is `b09ab7130752ae0c562b63ba04d2b1bea42f1e168c060f13d6e86e9bba277b84`.

## F10 Current Delivery Evidence

The previous F09 `SELF=5925c02` and F10 R4 `SELF=64bbea9` FINAL/CLEAN
statements are invalid. The runtime production source remains
`6abbaf5273aace450972f6e99fe44a8f05307812`; R5 changes only the stress
measurement protocol and its deterministic test. The R5 measurement source is
`f12701f1efed66f70cd267c1c63fbc2d38f96b1d`, and its clean heavy-evidence
checkpoint is `1dd1dcd79e3bccbec72e01dc50c84bbc850e9d9d`. The clean checkpoint
used to declare the immutable canonical performance campaign remains
`043966e041e294b996a279215277d494b34e1702`. The final documentation-only
delivery commit is `SELF` and does not change runtime or measurement source.

### Deterministic corrections

- `807d2a5` contains behavior-only RED tests. On unchanged production source
  `45e6703`, all three failed in 0.83s for the required reasons: owner normal
  close overwrote a standalone Actor fatal with `None`; Guard returned an old
  epoch fatal; and the stress server had no phase-scoped business window.
- `6c344d4` makes normal `PushBuffer.publish_close(None)` skip the error slot.
  A non-None fatal remains the only possible slot write, so a stale normal
  close cannot overwrite it and the Actor fatal path still takes no Push
  condition or new shared application lock.
- `6c344d4` also snapshots `PoolRuntimeGuard._publication_snapshot` by object
  identity. Every non-None lock-free result returns only if that exact object
  is still current; otherwise the existing Guard-locked slow path rereads and
  resolves the complete current epoch snapshot. Guard -> resolver lock order
  is unchanged.
- `2aea276` gives each timed heartbeat phase a unique ID, exact starting
  business-request count and target. The server opens the measurement window
  on the first phase request and closes it immediately after sending the final
  phase response. A legal heartbeat before the disable fence remains visible
  in total observation but is excluded from business-window counts.
- `c5afeb4`, `d3e1153` and `6abbaf5` close the remaining measurement edges:
  the final response send and phase finish share a wire lock, snapshots fence
  that publication, failed final sends always decrement active business state,
  and deterministic tests cover post-send and failed-send windows.
- Exact-final review then overturned `64bbea9`: R4 inferred the final response
  from request sequence, but four connections can complete responses out of
  order. `a8cc5b3` proves on the real `_serve()` path that the actual last
  response could send while the phase wire lock was held. `f12701f` classifies
  every response belonging to the active phase and holds the same wire lock
  across each response send and finish. Therefore whichever response actually
  closes the window is serialized with heartbeat classification and snapshots.

| Gate | Result | Artifact / identity |
| --- | --- | --- |
| F10 RED/REEN | Original RED `3 failed in 0.83s`, GREEN `3 passed in 0.25s`; R5 out-of-order RED `1 failed in 0.54s`, final GREEN boundary set `4 passed in 0.39s` | Original RED `807d2a5`; R5 RED `a8cc5b3`; fixes `6c344d4`, `2aea276`, `f12701f`; deterministic coverage `027935a` |
| New tests, 20 independent processes | final R5 `80/80` cases PASS in 20 processes; R4 `80/80` and earlier runs retained | R5 four boundary nodes, no failed process; R4 log SHA256 `5C403A6BD8E404D9C4405F8C0986E2968F8169F8299D20C4C9F502282980A0F3` |
| Targeted Push/Guard/heartbeat/retirement/lifecycle/stress | `263 passed in 239.78s (0:03:59)` | exact R5 test source `027935a`, runtime source `f12701f`; no retry |
| Complete pytest from zero | `652 passed in 246.80s (0:04:06)` | Windows 11, Python 3.12.6; exact final test set, no result splicing or retry |
| 10k generations / 100k requests stress | PASS; unique 10,000/100,000; duplicate/missing/unexpected/cross-request/cross-generation all 0; max active 4; leases/waiters/pins/frames/bytes/Actor threads 0; owned resources closed; resources `192,192,192,192,192,192,192,192`, plateau=true | clean exact source `1dd1dcd`; `<repository-root>/artifacts\actor-stress-f10-r5-1dd1dcd.json`, 744,495 bytes, SHA256 `9B7CF774E8E488715EF6C0DD5397EDB5E854B1B78EA0399783D985386C59DF39` |
| Heartbeat hard gate | PASS; both business-window totals 0; throughput ratio `0.998671`; 35,232 unique responses and all ownership counters 0 | R5 stress artifact; 32 unique timed phase IDs, exact start/target counters, phase-wide send/finish/snapshot fence |
| Close/resource hard gates | PASS; idle/loaded p99 `2.9323/2.7259ms`; idle CPU ratio 0; every measured resource sample 192 | R5 stress artifact |
| Paired performance campaign | **FAIL, user-approved exception**; exact 8-cell ABBA+BAAB, attempt=1, `errors=[]`; sequential ratio `0.943299`, saturated ratio `0.942391`; sequential p50/p99 PASS, no-backlog p50 PASS and p99 FAIL | canonical 11-file set in `<repository-root>/artifacts\perf-f10-043966e`, 99,990,158 bytes; declaration canonical SHA256 `cbb644f1104a606bc4c4103b3fe01c8fec872ad26bb448d8fd67f1a099c5973d`; bundle SHA256 `B1E4930BE5CF4A7CB421C015DE48AD4E2521860D67865E7C53C7D85266DBE3D3`; verification report SHA256 `64FD696DE85154ECD3B0C5A0FBF614DBB38D25AC23C474B462409985C98F5D8E`; canonical manifest SHA256 `6560AA2A95B0A476AD5A97006F907672CE797298FDC8963B3C51126EE48B0F16`; later independent report is external review output and excluded from this canonical set |
| Package artifacts | PASS; `python -m build` and `python -m twine check` | final R5 wheel 313,645 bytes, SHA256 `F899A9CC317DA91E12ACBBB72DC655E89967162FDFC5A5D9B1006FF5F85BA307`; sdist 381,212 bytes, SHA256 `18CFE96867C03D3DF2938EEAF677236A46966131C6874F587154DCFE8BEBA486` |
| MkDocs strict | PASS in 2.52s; 126 files, 5,685,815 bytes | R5 site artifact under `artifacts/site-f10-r5-1dd1dcd` |

An additional R5 performance campaign was declared once against baseline
`71089c0` and clean current source `1dd1dcd`, schedule ABBA+BAAB, declaration
identity `aaa6bb88196eabea17b13109e980c273c1613e4836a6a369f8d8f896ce2db247`.
Its first three attempt-1 cells completed, then declared cell 4 (index 3,
baseline) exited with Windows `RPC_NT_INTERNAL_ERROR` (`0xC0020043`). The
campaign stopped as required and was not retried, completed, or used for
ratios. The five retained files total 18,794,227 bytes; declaration file
SHA256 is `EB53AB4515B838E5FAD71A5A07FD48B2BD98F8CC94FD83D178944508FFA39A3D`
and failure record SHA256 is
`18CE3367B28285BAAC0E2D51FC98116008ACD4D0C39AD75A29DA0013F75E804A`.
This aborted diagnostic cannot replace the canonical campaign. Runtime source,
`benchmark_actor_transport.py`, `verify_actor_performance.py`, and
`pyproject.toml` have no `043966e..1dd1dcd` diff, so the canonical campaign
continues to describe the unchanged performance-sensitive implementation.

The F10 formal campaign retains the historical verdict exactly as **FAIL,
user-approved exception**. Its failed comparison gates are not reclassified,
no new exception was added, and no trial, threshold, sample count or raw datum
was replaced. The F10 races and measurement-only change do not alter the
revision 1.2 architecture authorization.

## Historical Delivery Evidence

The following table retains the prior exact-`3589a09` evidence for audit; it
is not substituted for the F09 results above.

| Gate | Result | Artifact / identity |
| --- | --- | --- |
| Deterministic retirement regressions | 43 passed; 20 independent processes each passed all 43 | RED `ee077cc`/`12ea212`; log `<external-artifacts>/actor-retirement-20proc-3589a09.log`, SHA256 `70F1ABA6EEB3C5EC8556CDCE6AF135AFCF82B57E363936B6E8E7B1E8EFA98DC1` |
| PushBuffer and full transport matrix | 431 passed in 15.82s | exact local source `3589a09` |
| Complete pytest | 641 passed in 254.29s (0:04:14) | no failures, xfail, rerun policy, or unaccounted skip in the run |
| 10k generations / 100k requests stress | PASS; unique 10,000/100,000, duplicate/missing/unexpected/cross-request/cross-generation all 0; max business active 4 | `<external-artifacts>/actor-retirement-stress-3589a09.json`, SHA256 `656AB99DAA6859DF763954529D048210AC293FDBC8AF2CE9CA4BEAAC6EED47EC` |
| Stress close/resource hard gates | PASS; leases/waiters/pins/frames/bytes 0, Actor resources closed, Actor threads 0, measured resources `188,188,188,188,188,188,188,188` | implementation SHA exact; `worktree_dirty=false`; workload SHA `487b3131af237b5843fe04046d51b60f136d6e22815297e29347286f93c3ea0a` |
| Prospective seven-pair performance | PASS; 14 attempt-1 trials, 1,750,000 raw rows, integrity errors `[]`, no retries or overlap | `<external-artifacts>/retirement-perf-f08-3589a09`, 20 files / 176,145,371 bytes; manifest SHA256 `29B12B410E5790BF2E0679BB8CBE6D3079E73788A0D95D8657FC08E9346BE910` |
| Performance gates | PASS; sequential ratio `0.9980727800`, saturated ratio `0.9988405873`, saturated p50/p99 `0.9999679624/1.0138644663`, no-backlog p99 delta `-61,200ns` <= `1,000,000ns` | baseline `45d8bc80f65eb57ee4ff5fab9a420d80aa705c6a`; current `3589a09095c21908dd738e266e295393b91548e8`; declaration SHA `fa5e80b616ff299b89261ba1c2fd6a86417d6428c30e6ae56a35ad7c9c16f636` |
| Package artifacts | PASS; `twine check` passed wheel and sdist | wheel SHA256 `40BB44ABCB3B30F6EB3158F9912C0CE3161796BD196A92435338C5D28CC93E54`; sdist SHA256 `EE06E7E607ED325BB08849F3C923B8BF115D24AED1E5795A410C30CB4F7634E0` |
| MkDocs strict | PASS | site artifact `<external-artifacts>/site-3589a09` (126 files, 5,685,815 bytes) |

The historical Actor-vs-legacy formal campaign remains **FAIL, user-approved exception**.
The current prospective campaign passed every frozen gate and does
not add or conceal a performance exception. The current run log SHA256 is
`0F452F7E324FF006C6AAFC98F29C413819032432171D6FCD07CFF34165BA6862`;
the policy report SHA256 is
`ECDC71F4BA52DFAB3EBC851A48ABF103968F14FF1AAD104DA3CC48CE85D70100`;
and the campaign bundle SHA256 is
`2A81903CC1F0CF9478F37AC7AC643204386A722D202E312F0EDC81D3AC1623B6`.
The external verifier copy records the restored 14-cell protocol, verifier
SHA256 `ba6ef1f838105f44339c2d747a7a4b3a7f1cb97a3df44fe9273f2767bd1ffa04`,
and unchanged repository producer SHA256
`b09ab7130752ae0c562b63ba04d2b1bea42f1e168c060f13d6e86e9bba277b84`.

The exact pre-final CI correction for `bc6990a8b0e6f350ef46ac2884930720fdd5a338`
passed all six required jobs in [CI run 29645035813](https://github.com/electkismet/eltdx/actions/runs/29645035813):
Ubuntu Python 3.10, 3.11, 3.12 and 3.13, plus Windows Python 3.11 and 3.13.
The same exact head passed the strict Pages build in [Pages run 29645035809](https://github.com/electkismet/eltdx/actions/runs/29645035809).
The preceding CI run `29644585790` failed only Windows Python 3.13 because
`runtime.stopped` was set before the Actor thread target returned; `bc6990a`
keeps one absolute 0.2-second budget across the stop Event wait and remaining
budget `join()`. The gate was not widened and no test was weakened.

## Cross-Platform CI and Builds

The preceding external-lock source `abd58c39aef6f905075788d4482eac43e673ba63`
historically passed [CI run 29577023570](https://github.com/electkismet/eltdx/actions/runs/29577023570):

| Platform | Python | Result |
| --- | --- | --- |
| Ubuntu | 3.10 | 597 passed, 1 Windows-only skip in 290.38s, SUCCESS |
| Ubuntu | 3.11 | 597 passed, 1 Windows-only skip in 278.27s, SUCCESS |
| Ubuntu | 3.12 | 597 passed, 1 Windows-only skip in 286.35s, SUCCESS |
| Ubuntu | 3.13 | 597 passed, 1 Windows-only skip in 283.02s, wheel/sdist build SUCCESS |
| Windows | 3.11 | Full suite, 598 passed in 251.36s, SUCCESS |
| Windows | 3.13 | Full suite, 598 passed in 244.21s, SUCCESS |
| Pages | [run 29577023585](https://github.com/electkismet/eltdx/actions/runs/29577023585) | strict build and artifact upload SUCCESS |

The exact `bc6990a8b0e6f350ef46ac2884930720fdd5a338` correction head also passed
[CI run 29645035813](https://github.com/electkismet/eltdx/actions/runs/29645035813)
and [Pages run 29645035809](https://github.com/electkismet/eltdx/actions/runs/29645035809).
This six-job matrix reported the full local source-equivalent suite green; the
current full local verification after the correction is `638 passed in 255.01s`.

The later FINAL candidate `d38bfc6bd2d30336e2a222b3ee2a6cb2b366edec`
passed [CI run 29645265072](https://github.com/electkismet/eltdx/actions/runs/29645265072)
and [Pages run 29645265073](https://github.com/electkismet/eltdx/actions/runs/29645265073),
but independent final review then reopened it. Those green runs are historical
evidence only and are not exact-source proof for production `3589a09` or final
delivery `SELF`.

The exact preceding FINAL checkpoint `ac942a87cd1f1fd78b5486bc29660361c7af380e`
passed [CI run 29648788642](https://github.com/electkismet/eltdx/actions/runs/29648788642)
and [Pages run 29648788648](https://github.com/electkismet/eltdx/actions/runs/29648788648).
The final documentation-only manifest that follows it is a new exact HEAD and
must pass its own CI/Pages runs before delivery is claimed.

The Windows jobs run the full suite, including all correction regression files
and the real Windows refused-first `connect_ex` test. Pages deployment remains
intentionally skipped for a pull request; the site build is the required gate.

The test-marker audit found one conditional skip only:
`test_windows_refused_first_address_reaches_healthy_backup`, guarded by
`sys.platform != "win32"`. It accounts for the single Ubuntu skip and runs on
both Windows jobs. Windows has zero skipped tests. There are no xfail or flaky
markers, plugins, rerun rules, or intermittent-failure allowlists masking a
failure.

This historical matrix is not exact-source proof for `721cbe8` or final
`SELF`. Delivery requires a normal push followed by SUCCESS for Ubuntu Python
3.10-3.13, Windows Python 3.11/3.13, package build/twine and Pages strict on the
exact final `SELF`; the resulting run URLs are retained in the external
checkpoint and final report.

The `71089c0..e924d4d` scope review covers the original 39 changed files. The
later `e924d4d..abd58c3` correction is limited to two result/progress records,
four 7709 transport modules and five transport regression files. The
`f5b63bb..721cbe8` epoch-retirement correction changes only this result record,
two transport modules, one retirement regression file and the two transport
operator documents.
Project runtime
dependencies remain exactly `dependencies = []`; no 7615 implementation or
business-command facade was changed. The `client.py`, host and registry edits
are bounded 7709 transport integration/validation changes, while the two MCP
test edits only prevent their context-manager fixtures from opening a real
7709 connection. Workflow changes add the required Windows matrix; MkDocs and
Pages changes are limited to Actor architecture, API, debugging and changelog
content. No unrelated Pages content, release metadata or publication path was
added. An independent scope/CI reviewer reached the same conclusion.

## Review and Completion Audit

- Two independent control-path reviews found the heartbeat, connect and
  terminal-ownership gaps after the performance exception. Every finding was
  reproduced, fixed and rereviewed CLEAN against `3287b6a`; implementation,
  lock order, retry/failure behavior and regression mapping are clean.
- An earlier audit of the now-deleted heavy JSON reported clean reconciliation;
  it is historical only and cannot support the reopened correction.
- A fresh correctness/manifest reviewer found production code CLEAN and ran
  253 key A-E regression nodes in 14.13s. Its two manifest findings (exact
  procedural-spec identity and permanent reproduction-node mapping) were fixed;
  the independent rereview confirmed both fixes CLEAN and validated every node
  named in the permanent A-E/control table.
- A separate fresh scope/CI reviewer returned CLEAN for exact `e924d4d`: all 59
  earlier first-parent checkpoints were accounted for, CI/Pages and marker
  audits reconciled, PR/scope/dependency constraints held, all detached
  worktrees were clean and no task-owned process was running.
- Final review at `f5ad8a3` reproduced an old-settler/new-publication clear
  race; the next Actor review at `166ae61` reproduced the stale timeout
  fallback overwriting a newer call. Both blockers became behavior-only red
  tests and were fixed before `abd58c3`; neither older exact-head green run is
  used as FINAL source evidence.
- The final Actor/nonblocking reviewer returned CLEAN for exact `eac784b`
  (production source exact `abd58c3`) and ran 20 external-lock/pin/FIFO nodes
  with cache/bytecode writes disabled. It found no Pool/Broker/Proxy/Push or
  sibling-lock wait on Actor paths and no stale cell ownership.
- The independent Pool/pin/lifecycle reviewer returned CLEAN for the same
  source after auditing Broker FIFO, lease publication, fatal epochs, pin
  settler/close/cancel/capacity, startup rollback, shutdown monotonicity and
  lock order; independent reruns were 85 Pool and 92 lifecycle passes.
- The independent evidence rereview reconciled the uncontaminated `l03rr2`
  files, CB82 stress, package hashes, exact CI/Pages logs, formal schema-4 FAIL
  and architecture exception. Its findings on schema-2 quantile aggregation,
  scope count, line-ending hashes and stale result identity were corrected;
  after actual cleanup, the final line-by-line rereview returned CLEAN.
- Independent review of `d38bfc6` found that Guard could expose an unpublished
  `runtime.fatal_error`, an owner-selected failure could later be replaced by
  an Actor cell, and a no-error deferred Push abandon could retain frames. The
  three behavior-only regressions failed deterministically before `3589a09`;
  after the correction, retirement/Pool review reran 128 nodes and
  push/client/socket review reran 45 nodes and returned CLEAN.
- The first independent F10 code reviewer returned CLEAN for exact `043966e`:
  Push and Guard linearization, fatal hot-path locking and resolver lock order
  had no P1/P2/P3 finding. Independent runs included 132 retirement+Pool nodes
  and 20 processes / 40 new race cases, all passing.
- The second independent R4 code reviewer returned CLEAN for the reviewed
  ordinal-final send/finish, snapshot and failed-send edges, but exact-final
  rereview then proved that request sequence does not determine response
  completion order. That later P1 finding overturned `64bbea9` and is the R5
  correction above; the earlier R4 CLEAN conclusion is not current evidence.
- The independent evidence reviewer returned CLEAN after correcting one P3
  wording issue: the performance directory is explicitly reported as a
  canonical 11-file set, while the later `independent_report.json` remains
  external review output and is excluded from the canonical manifest/hash.
- Two independent R5 code reviews found the phase-wide production wire fence,
  Push and Guard CLEAN. They found one P3 and one P2 only in permanent test
  strength: a 50ms negative scheduling assertion and missing real `_serve()`
  proof across send-to-finish plus failed send. `ff3b1e0` and `027935a`
  replaced the timing assumption with positive lock-attempt latches, block
  heartbeat and snapshots inside a real out-of-order closer send, assert finish
  callback ownership of the wire lock, and exercise real raising-send cleanup.
  The final four nodes passed 80/80 in 20 processes,
  the exact targeted matrix passed 263 nodes, and the full suite passed 652.
- Final exact-source reconciliation at `4c02ce0` found no remaining P1/P2/P3:
  both independent reviewers' production-code CLEAN conclusions still apply;
  their P3/P2 permanent-test findings are covered by the committed positive
  latches and owner assertions. The R5 artifact audit rechecked the clean
  stress JSON, aborted performance disclosure, final package bytes/hashes,
  Plan identity and MkDocs counts against their retained raw files.
- Current FINAL cleanup retains the primary worktree plus clean detached
  `f5b63bb`/`721cbe8` performance roots so
  the retained campaign verifier can replay their exact absolute identities;
  `git clean -nd` is empty. Ignored local pytest/bytecode caches are not a
  delivery artifact and are deliberately not claimed empty. No task-owned
  Python, pytest, benchmark, stress or MkDocs process remains. The retained
  raw JSON/campaign and final dist/site evidence under the external artifact
  directory are deliberate.
- The FINAL commit must have no progress ledger, no untracked non-ignored file,
  no task-owned process, and two or more clean independent review conclusions.
- Local HEAD, remote branch, PR head, FINAL CI, and FINAL Pages must all resolve
  to `SELF` before completion is claimed.

## Remaining Documented Limits

- Standard-library DNS for a previously unseen custom hostname is a documented
  caller-side preflight and cannot be cancelled reliably. It owns no Actor,
  lease, or TCP resource; numeric/cached endpoints use the full deadline.
- Finalizers are best-effort non-blocking stop/wakeup fallbacks. Deterministic
  release requires explicit `close()` or a context manager.
- Loopback performance isolates transport scheduling. Real exchange latency is
  outside this refactor and is not represented as a benchmark claim.

The PR remains intentionally unmerged and draft. No tag, release, main update,
or package publication was performed.

The temporary `ACTOR_REFACTOR_FIX_PROGRESS.md` ledger is deleted by the
first-parent FINAL finalization commit containing this manifest. Future
recovery must use this manifest and Git history rather than recreate the ledger.

## Recovery Rule

Resolve `SELF`, verify branch/PR identity and exact-SHA checks, then use this
manifest and the Git history as the authority. Do not recreate the temporary
correction ledger after FINAL. If any later commit exists, audit it and its
checks before relying on this result.
