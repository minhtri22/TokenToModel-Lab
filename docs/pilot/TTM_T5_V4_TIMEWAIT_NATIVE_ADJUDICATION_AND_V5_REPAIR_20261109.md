# TTM T5 — V4 native HOLD / TIME_WAIT root cause and V5 scoped repair (2026-11-09)

## Key evidence
- User's V4 native run passed source/PS5.1 checks and 35/35 mock QA. `127.0.0.1:12647`, Ollama 0.40.14, spawned PID 34192.
- `READINESS_ATTEMPTS.jsonl` has 4 attempts: `WAIT_NO_CANDIDATE_SOCKET`, `WAIT_HTTP_NO_200` twice, and `HOLD_OWNER_CHANGED_AFTER_HTTP` on attempt 4.
- On attempt 4 HTTP version check **succeeded**: HTTP 200, `{"version":"0.40.14"}`. Before and after HTTP the listener-candidate row remained `127.0.0.1:12647 / pid=34192 / state=0 UNKNOWN / remote=0.0.0.0:0`.
- After HTTP a *second, transient connection* appeared with `pid=0 / state_code=11 / remote=127.0.0.1:53457`. Per Microsoft Learn `state_code=11` is **TIME_WAIT**, not LISTEN. Source `tcp_table_observation` required a single positive PID across all rows, and `ownership_status` rejected any `pid<=0`, so it suppressed otherwise valid identity and returned `HOLD_TCP_ROW_MALFORMED`. This was reported as `READINESS_HOLD_OWNER_CHANGED_AFTER_HTTP`, **not proof that server PID changed**.
- After owned-process shutdown, `shutdown_tcp_table` contained just that same `pid=0 / state=11 TIME_WAIT` row. V4's cleanup logic set final status `HOLD_ANY_TARGET_PORT_ROWS_REMAIN_AFTER_SHUTDOWN`, overshadowing the original readiness failure. Shutdown itself reported `STOPPED_OWNED_TREE`, taskkill 0.
- V4 has `models_after_run={}` and only stage `server_started`: **Ollama create and inference were never executed**. Original GGUF/FAIL receipts remain unchanged. `T5_FULL_LOGITS=FAIL_7_OF_8_PRESERVED`.

## Technical correction
- V5 is a **new** immutable one-shot identity and not a rerun of V1, V2, V3 RC1, or V4: port 12648, local store `_tmp/ttm_t5_ollama_compat_only_single_v5final`.
- Resolve process identity from listener candidates only (state 0 UNKNOWN or state 2 LISTEN, null remote endpoint). Keep `state=0` as UNKNOWN, never relabel as LISTEN.
- Permit a **narrow harmless remnant** of `pid=0/state=11 TIME_WAIT` solely when both local and remote addresses are matching loopback and the remote port is nonzero. Ignore these rows for listener-owner matching and post-shutdown cleanup **only**. Reject foreign candidate PID, non-loopback or wildcard, other zero-PID state, and active listener after shutdown.
- Before importing GGUF require the same process PID, exact executable path/creation time, source/hash pins and HTTP 200 exact version both before and after TCP sampling. One shot per fresh directory; no retry on failure. Import and inference limited to project-local model store and 32 tokens.
- 47/47 tests passed in assistant container, including actual V4 trace-shaped regression, negative PID0 cases, and full mocked Ollama model import/generate with benign TIME_WAIT after shutdown. **Windows V5 QA and native Ollama V5 are NOT_EXECUTED.**
- V5 source bundle SHA256 `0c27593dd01c5e652709c03b6a0019533aa602e178d1e4251052bc69bf01ef33`. Individual source pin hashes recorded separately in JSON. Bundle distributed in conversation and **not yet committed as source bytes**; do not claim otherwise.

## Decision
`V4_ONE_SHOT=CONSUMED_NO_RERUN`, `V4_READINESS=FAIL_TECHNICAL_TIMEWAIT_CLASSIFICATION`, `HTTP_VERSION=PASS`, `OLLAMA_IMPORT=NOT_EXECUTED`, `MODEL_COMPATIBILITY=NOT_ESTABLISHED`, `V5_OFFLINE_QA=PASS_47_OF_47`.
Do not merge PR #12, modify `main`, append technical QA to `lineage.md`, alter checkpoint/GGUF, or use ordinary port 11434.

**Next**: `TTM_T5_V5_TIMEWAIT_GUARDED_ONE_SHOT_WINDOWS_RUN_AND_MODEL_COMPATIBILITY_ADJUDICATION` with a guarded user-invoked V5 wrapper, conditional on all SHA/preflight checks passing.

Reference: https://learn.microsoft.com/en-us/windows/win32/api/tcpmib/ns-tcpmib-mib_tcprow_owner_pid
