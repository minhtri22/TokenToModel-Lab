# TTM FRESH16 V2 — Single Integrated Agent Handoff & GO/NO-GO Readiness

**Operation:** TTM_FRESH16_V2_SINGLE_CPU_RUNNER_BLIND_MAP_RATER_CUSTODY_INTEGRATED_GO_NO_GO
**Date:** 2026-11-11
**Research branch:** research/ttm-small4m-prompt-adherence-continuation-design-20261111
**Source baseline:** 39c1cbfb8734911a3d9fba0e7249e1c3985f94a0
**Owner V2 status:** ADOPT_V2 (explicit owner message, self-attested no prior output exposure).
**Science mode now:** NO MODEL FORWARD — NOT EXECUTED.
**Current single decision:** NO_GO_HOLD pending executor implementation, sealed mapping and actual independent sessions; no repeated source QA gates.

## 1. Exactly three agent jobs — send separately

| Role | Handoff file | First response expected | Writes allowed |
|---|---|---|---|
| E0 CPU Executor + Blind Map Builder | docs/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_AGENT_E0_CPU_RUNNER_BLIND_MAP_HANDOFF_20261111.md | Source-only runner implementation/commit, map custody plan or privately sealed map, one readiness receipt | **Only E0** may commit new executable source to FRESH16 research branch; no inference until owner GO |
| S1 Independent Individual Rater | docs/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_AGENT_S1_OUTPUT_RATER_HANDOFF_20261111.md | READY_FOR_S1_PACKET + actual rater identity/version/session; later exact 32 scores | Read-only; no source edits or pairing |
| S2 Independent Pair Adjudicator | docs/research/ttm-small4m-quality-gap/TTM_FRESH16_V2_AGENT_S2_PAIR_ADJUDICATOR_HANDOFF_20261111.md | READY_FOR_S2_PACKET + actual identity/version/session; later exact 16 pair scores after S1 lock | Read-only; no source edits or checkpoint access |

Do NOT send this coordination document to S1/S2 as their scoring packet. Share **only their own handoff URL**, then their respective private packet in the correct order. S1 and S2 must be in different fresh sessions and separate from Executor and earlier independent Protocol Reviewer. Their role cannot be claimed assigned merely because a file exists.

## 2. Immutable scientific inputs

- Original 16 prompt bytes, Git blob 6299a073f0b7c7f8ea890ba9d9b29eaed9442f1f.
- Original frozen rubric/H1≥12/16, H2≥6/8 & ≥1 H2 pass each of four groups: Git blob 69668664df23d2246cd65935ab049054aea43e7a.
- Adopted V2 outcome definition Git blob 27b994b3b3283b2611af21d63acc5d37abf45013.
- Original source QA native Windows: PASS 11/11 and TRAIN-only BPE 16/16; SHA checkpoint step1024 and 1280 PASS per receipt. No rerun unless source drift.
- P02 original source Git blob 9762343e06cf800b50574c2871ae1ed58537fb18.
- Science budget frozen: 32 outputs total, 16 each checkpoint, greedy, max64 generated tokens, context256, CPU only, no training, no TEST, no retry. Step1024 primary / step1280 descriptive only.

## 3. Single combined readiness adjudication

| One-time integrated criterion | Current state | GO requires |
|---|---|---|
| Frozen prompt/rubric/V2 source bytes | PASS_RECORDED | Exact SHA pins unchanged |
| Owner V2 adoption and no-exposure | ADOPTED_OWNER_ASSERTED | Preserve original owner message receipt, do not demand redundant attestations |
| Exact trained 4M P02 checkpoint/config loader | NOT_YET_PINNED_FOR_RUN | E0 strict source/weight compatibility without inference |
| CPU future one-shot runner SHA and no-retry safeguards | NOT_IMPLEMENTED/YET_VERIFIED | Source-only code reviewed and pinned; finite caps |
| Cryptographically shuffled 32-map with private custody | NOT_CREATED | Create local-only sealed map and anchor private map hash before inference |
| Actual S1 identity/version/session | NOT_INSTANTIATED | A new independent rater accepts assignment |
| Actual S2 identity/version/session | NOT_INSTANTIATED | A distinct independent pair adjudicator accepts assignment |
| Output and packet integrity contract | SPEC_PREPARED | E0 produces schema validators and no-label-leak checks |
| One owner science permit | NOT_ISSUED | Distinct explicit single GO after all above, not inferred from ADOPT_V2 |

**Current authoritative conclusion: NO_GO_HOLD_FOR_CPU_INFERENCE.** This is not FAIL of science, not FAIL of model and not a request for extra source-only QA. The missing pieces are actual implementation and role/session custody.

## 4. Exact one-way workflow after GO, not today

1. E0 seals mapping and anchors its hash before any model forward; source and permits pinned. Run exactly 32 outputs once, store originals privately, do not publish secret mapping.
2. E0 hands S1 only 32 opaque prompt+generated_text records; S1 returns 32 individual scores. SHA-lock and **commit S1 hash receipt** before revealing pairing.
3. E0 hands S2 only 16 opaque pairs with locked S1 scores, still hiding checkpoint identities. S2 returns 16 fact-sensitive classifications; SHA-lock and **commit S2 hash receipt** before unblinding.
4. Owner opens private map only after both SHA receipts are independently anchored, tallies frozen H1/H2, appends actual scientific PASS/FAIL to lineage.md only when an experiment has genuinely run and been adjudicated (not now).

Do not force-push, delete worktrees, rerun old TEST/one-shots, use generated example model text in public docs or create toy science results. Resolve missing work in **one combined E0 receipt** instead of chains of micro-permits.

## 5. Deliverable for owner after agents' source-only responses

One compact result from E0: RUNNER_SHA / MAP_SHA / S1_SESSION / S2_SESSION / SOURCE_QA_REUSED / runtime cap / `GO_CANDIDATE` or `NO_GO_HOLD`. The owner will separately decide `GO_32_CPU_ONE_SHOT` or `NO_GO_HOLD`, without requesting another protocol reviewer pass.

**Bước thực hiện tiếp theo:** send each handoff to its corresponding agent; collect E0 source-only readiness and S1/S2 session identity, then make **one** science run decision. **No science executed by authoring these handoffs.**
