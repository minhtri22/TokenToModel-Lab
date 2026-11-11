# TTM FRESH16 V2 — E0 CPU Runner, Blind Map & One Integrated Readiness Gate

**Operation:** \`TTM_FRESH16_V2_E0_PREPARE_RUNNER_SEALED_MAP_SINGLE_READINESS_GATE\`
**Date:** 2026-11-11
**Branch:** \`research/ttm-small4m-prompt-adherence-continuation-design-20261111\`
**Before E0:** \`89dcbe1af040802472428ed73eaf2b4e030013b0\`.
**Owner V2:** ADOPTED (Git blob \`27b994b3b3283b2611af21d63acc5d37abf45013\`).
**Overall:** \`E0_SOURCE_IMPLEMENTATION_COMPLETE\` / \`WINDOWS_PRIVATE_PREPARE_NOT_EXECUTED\` / \`SCIENCE_NO_GO_HOLD\`.

## 1. New source-only implementation

- \`tools/research/ttm_small4m_quality_gap/ttm_fresh16_v2_e0.py\`: **prepare** validates source Git pins, exact real TRAIN-only BPE2048, both checkpoint file sizes + SHA, checkpoint \`config\`, step metadata, P02 source and strict \`load_state_dict\` without model forward. It creates a project-local sealed 32-output/16-pair randomized map with 128-bit opaque IDs and a private 256-bit nonce; writes an exclusive private map and one PREPARED receipt.
- Its **run** mode is a separate, explicit gate: needs an owner-issued \`GO_32_CPU_ONE_SHOT\` permit with SHA, exact source HEAD/runner blob, S1/S2 session IDs and a private map SHA anchored by a Git commit. Creates \`RUN_STARTED.json\` **before** forward and refuses any retry. CPU, FP32, greedy; maximum 64 newly generated tokens × 32, context 256, EOS 256, wall cap 900 s, process working set 8 GiB, fsynced raw output receipts. No TEST/TRAIN/VAL read.
- \`ttm_fresh16_v2_packet_gate.py\`: S2 packet cannot be assembled until 32 S1 grades are complete, schema/evidence-validated and their SHA-256 has been anchored in a Git commit. Final tally only after 16 S2 pairs are complete and the S2 SHA-256 has also been Git-anchored. Do not give S1/S2 this public coordination document as part of their blinded packets.
- \`Invoke-TTM-Fresh16-V2-E0-PS51.ps1\`: one PowerShell 5.1 wrapper with \`Prepare\` as the default, exact research HEAD and Python 3.12; \`Run\` requires all explicit permit arguments.
- \`test_e0_source_only.py\`: static/source-only mapping, randomization, tamper rejection, absent-permit fail-close, and exact step1280 metadata/SHA check when original binary is mounted.

**Source P02 code Git blob:** \`9762343e06cf800b50574c2871ae1ed58537fb18\`. Trained checkpoint config is **explicitly** \`vocab_size=2048, max_seq_len=256, n_embd=256, n_layer=4, n_head=4, norm_type=layernorm\`, unique parameters **3,749,376**, not P02Config's tiny engineering defaults.

## 2. Evidence obtained this turn (no inference)

- Python 3.13 local source compilation: \`PASS\` on both new Python files (programmatic syntax only, not Windows native verification).
- Local isolated source-only tests: **5/5 PASS**. No model forward; this is **not** the owner's native Windows Python 3.12 integration QA.
- Original step1280 full raw binary was loaded with \`torch.load(..., weights_only=True, map_location='cpu')\`; SHA256 **ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc** matches the frozen pin, and checkpoint metadata contains config above, \`step=1280\`, P02 source blob, 53 state_dict entries, 3,749,376 unique weights and parent checkpoint SHA **cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b**. No forward.
- Existing owner Windows QA receipt (prior) had **11/11 PASS**, real BPE roundtrip 16/16 and local checkpoint SHA 2/2. These older source gates were **not rerun**.
- Remote Windows node was used only for list/read checks. Arbitrary \`run_command\` returned \`managed mode requires task_job_submit\`; no project task lease was opened to create a micro-permit for a source-only check.

**Evidence boundary:** Windows \`prepare\` has **NOT** run. Therefore **do not claim** \`E0_NATIVE_WINDOWS_PASS\`, \`MAP_SEALED_ON_WINDOWS\` or \`CPU_RUN_GO\`.

## 3. Exactly one Windows source-only PREPARE command

First fast-forward the correct clean research worktree to the E0 commit, **never** force/reset or touch main. Use the exact E0 commit SHA copied from the GitHub commit link (avoid bare branch HEAD if another agent has moved it). Then from PowerShell 5.1:

~~~powershell
$root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$wt = Join-Path $root 'worktrees\ttm-fresh16-quality-20261111'
$expected = '<EXACT_E0_COMMIT_SHA_FROM_GITHUB>'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (
    Join-Path $wt 'tools\research\ttm_small4m_quality_gap\Invoke-TTM-Fresh16-V2-E0-PS51.ps1'
) -Mode Prepare -ExpectedHead $expected
~~~

The script will fail closed if \`_tmp/ttm_fresh16_v2_e0_20261111\` already exists, if the worktree is dirty, or if source/checkpoint/manifest bytes drift. **Do not delete or rerun the same one-shot preflight directory automatically**. If it succeeds, private \`BLIND_MAP_PRIVATE.json\` + \`PREPARED.json\` exist inside project \`_tmp\`; only report SHA and status, never upload map to public GitHub.

Expected console markers after success (not yet observed):
\`FRESH16_E0_PREPARE=PASS_SOURCE_ONLY_NO_FORWARD\`
\`FRESH16_E0_MAP_SHA256=<actual_sha>\`
\`FRESH16_E0_RUNNER_GIT_BLOB=<actual_blob>\`
\`FRESH16_E0_EXECUTION=NO_GO_HOLD\`.

## 4. Handoff to owner before S1/S2 are activated

Current required single gate: native Windows PREPARE readback, map SHA anchored in a new Git commit under \`artifacts/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_PRIVATE_MAP_SHA_ANCHOR.json\` with \`source_head\` and \`sealed_map_sha256\`; owner creates S1 and S2 separate sessions and records exact identity/version, then issues one *distinct* explicit \`GO_32_CPU_ONE_SHOT\` science permit only if ready.

Do **not** create a fake permit; \`ADOPT_V2\` was rubric adoption, not inference authorization. Do **not** run \`-Mode Run\` yet.

When the actual private 32-output batch exists following future GO:
- S1 sees **only** 32 shuffled \`opaque_id\`, \`prompt_text\`, \`generated_text_only\` records (not checkpoint or pair IDs).
- After S1 score SHA is anchored in Git, E0 uses \`packet_gate.py --mode package-s2\` to produce 16 checkpoint-blind pairs.
- After S2 score SHA is anchored in Git, E0 uses \`--mode unblind\` for frozen H1/H2 tally. No score or denominator modification.

**Decision in this E0 source-only turn:** \`NO_GO_HOLD\` due unobserved Windows PREPARE, uncommitted map hash, uninstantiated S1/S2 sessions, and unissued owner execution GO. It is not science FAIL. No new training/inference/TEST access. \`lineage.md\` append-only was left untouched.

**Bước thực hiện tiếp theo:** one single native Windows **PREPARE** invocation and receipt readback; then organize S1/S2 and one owner GO/NO-GO, without rerunning already-PASS original source QA.
