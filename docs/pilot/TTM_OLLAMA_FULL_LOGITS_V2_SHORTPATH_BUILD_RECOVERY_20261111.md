# TTM — Ollama full logits: Windows Git MAX_PATH recovery V2 (2026-11-11)

**V1 source/build failed before compile** at `01_git_worktree_add.log` with `Filename too long` and Git exit code 128. The original stage `_tmp/ttm_ollama_full_logits_candidate_build_20261111` contains exact failure log and receipt SHA256 `b7f0750541b872f0806ff5a4ab9a5cc9952f08830607fc6fa90bb29e4a944cb4`. Windows remote readback confirmed `llama` worktree directory absent after Git rollback. Do not delete V1.

## Recovery V2

Use `tools/ollama_full_logits_v1/stage_and_build_ollama_full_logits_v2.py`, with `--build`, after the research worktree is ff-only at the new commit. The new root `_tmp/fl2` lies wholly inside project. The previously failing example path drops from 262 to 218 characters. Git's `core.longpaths=true` is scoped only to the checkout command; no global Git settings are modified.

V2 validates the exact V1 failure receipt and log without cleanup, re-reads the entire frozen P02 F32 reference and SHA-seal, validates unchanged v5 source/runner, constructs a new short-path candidate via Git worktree, copies the exact four v5 postpatch source blobs, then applies V2 pre-sampler hook.

**Second proactive source correction:** original uncompiled hook used `vocab` in a scope where that identifier is absent. V2 hook obtains vocabulary using `llama_model_get_vocab(llama_get_model(slot.ctx_tgt))`. Neither previous `git apply --check` nor offline Python tests demonstrated C++ compilation. V2 still needs actual MSVC build to judge this code, and build failure must preserve evidence.

Compiled runner is installed only in `_tmp/fl2/package` (an isolated copy of original v5), with original Go CLI SHA check and distinct native SHA check. No model call/TEST/training, no main merge, no lineage update.

**Status at commit:** `V1=HOLD_WINDOWS_PATH_TOO_LONG` · `V2=PREPARED_NOT_EXECUTED` · `REFERENCE=PASS_SCOPED` · `OLLAMA_FULL_LOGITS=NOT_EXECUTED`.

**Bước thực hiện tiếp theo:** `TTM_OLLAMA_FULL_LOGITS_V2_SHORTPATH_NATIVE_BUILD_AND_RECEIPT_REVIEW`. Execute one V2 integrated build attempt, retain logs and SHA; don't replay V1.
