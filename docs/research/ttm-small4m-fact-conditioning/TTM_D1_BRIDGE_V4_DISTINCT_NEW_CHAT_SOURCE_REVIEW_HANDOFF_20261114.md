# HANDOFF — D1 Bridge V4, new-chat independent science design/source review

**Operation:** `TTM_SMALL4M_D1_BRIDGE_V4_DISTINCT_NEW_CHAT_TASK_RELEVANT_SOURCE_REVIEW_SINGLE_DESIGN_GO_HOLD_NO_GPU`  
**Date:** 2026-11-14 · **Repo:** `minhtri22/TokenToModel-Lab`  
**Frozen scientific/source input HEAD:** `1c923c0dc1a064411190392612e9d2475486bd2c`  
**Reviewer:** independent AI scientific design reviewer in a distinct new chat (not human, independence self-attested).  
**Mode:** `READ_ONLY / SOURCE_ONLY / DESIGN_ONLY / NO_GPU / NO_TRAIN / NO_INFERENCE / NO_EVAL_GOLD / NO_TEST_Q1Q2`.

## 1. Read mandatory frozen 7/7 sources

| Source at frozen scientific input | Expected Git blob SHA-1 |
|---|---|
| [V4 design Markdown](https://github.com/minhtri22/TokenToModel-Lab/blob/1c923c0dc1a064411190392612e9d2475486bd2c/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V4_SINGLE_PACKET_TASK_RELEVANT_OOD_PARSER_AUDITOR_CONTRAST_PREREG_DESIGN_HOLD_20261114.md) | `39f89d8fa111b3b15d34f47b4a776c61bc6e42a2` |
| [V4 machine JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/1c923c0dc1a064411190392612e9d2475486bd2c/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V4_SINGLE_PACKET_TASK_RELEVANT_OOD_PARSER_AUDITOR_CONTRAST_PREREG_DESIGN_HOLD_20261114.json) | `e89284318ce49c2cb0373dc37660216eb532904d` |
| [V4 same-author source QA JS](https://github.com/minhtri22/TokenToModel-Lab/blob/1c923c0dc1a064411190392612e9d2475486bd2c/tools/pilot_t4/fc01/ttm_d1_bridge_v4_source_only_contract_qa_20261114.js) | `d459882694651d5e8e8455c30abc0a90dba8e444` |
| [V4 source-only QA receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/1c923c0dc1a064411190392612e9d2475486bd2c/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V4_SINGLE_PACKET_SOURCE_ONLY_QA_AND_OWNER_HOLD_20261114.json) | `09eb5882c68e7cb45e82d4e4d85891ae0bdb31e4` |
| [Independent V3 review MD](https://github.com/minhtri22/TokenToModel-Lab/blob/1c923c0dc1a064411190392612e9d2475486bd2c/docs/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_DISTINCT_INDEPENDENT_PREREG_SOURCE_REVIEW_20261114.md) | `0ef0a578262daa6379a2b3af25d3a3c2e9b05fb8` |
| [Independent V3 review JSON](https://github.com/minhtri22/TokenToModel-Lab/blob/1c923c0dc1a064411190392612e9d2475486bd2c/artifacts/research/ttm-small4m-fact-conditioning/TTM_D1_BRIDGE_V3_DISTINCT_INDEPENDENT_REVIEW_RECEIPT_20261114.json) | `425260e35a3c2d798058ea35d8007144072bcbd3` |
| [lineage L0019](https://github.com/minhtri22/TokenToModel-Lab/blob/1c923c0dc1a064411190392612e9d2475486bd2c/lineage.md) | `c7eb0cfd417876b456ce3f5b4616c2d989a1f076` |

Verify exact Git blob SHA-1 metadata against each pinned source. Don't use a later branch HEAD. The V3 review originals were byte-checked before archiving (MD SHA256 `e806d03741c50d75a5e0ad910a1700c511c8057450384a5cad22cc94a96fd441`; JSON SHA256 `1a7421f992d80e778152f0a03434c358a4251f66716c5e910aefb890ded530c7`). Git blob SHA-1 is a Git-object hash, **not** SHA-256. Say what was actually verified.

V3 reviewer verdict: `HOLD_REVISE_BEFORE_PREREG`; 2 source-design PASS (AM03/AM04), 4 HOLD (AM01/02/05/06), 0 FAIL; 6 new findings `D1V3-N01...N06`, 11 inherited `D1V2-01...11`. V4 addresses all in a **new** contract only. It is not approved science and no AST/parser/custody/runtime QA has been executed.

## 2. Required independent adversarial axes

**R1 — AM01: task-relevant OOD (CRITICAL):** Compare V3 strong trace criterion vs V4 decision-policy on a fixed admissible input alphabet/finite reachable states. Are joint requirements `non-alpha-isomorphic causal skeleton` AND `reachable policy/goal-changing counterexample` actually sufficient to exclude lexical relabeling, inert internal traces, oracle cues, and trivial label shortcuts? Check correct treatment of same policy but different bookkeeping/selfloop, unreachable-only differences, priority/temporal/negation effects, and domain alignment. Challenge whether requiring action difference rules out meaningful process-only generalization; demand explicitly bounded scientific claim. Actual generator/checker `NOT_IMPLEMENTED`; no source PASS for real nonoverlap.

**R2 — AM02: explicit TIME and parser validity (CRITICAL):** Verify scored tuple `(agent,verb,target,time,qualifier)` vs grammar `AGENT VERB TARGET TIME (QUALIFIER)?` and optional frozen synonyms. TIME must be present in generated text; condition/witness cannot be supplied from gold at scoring time. Challenge grammar ambiguity, `TIME NONE` phrase handling, injectivity, wrong-condition parsing, false negatives for valid natural-language answers, and the meaning of constrained canonical-action generation vs unbounded free-form correctness. Review proposed independent synthetic QA criterion (>=64 positives, >=64 negatives, zero false accepts) **as a prospective gate**, not measured sensitivity/specificity.

**R3 — AM03: seed sign test (PASS in V3 only):** Check no new corruption of 12 seed values, signed integer `D_s`, strict positive `D_s>0`, `D_s=0` nonpositive, `k>=10/12`, exact `p(k=10)=79/4096`, iid and stochastic stream assumptions not empirically proven, and the fixed 16-skeleton-only inference. Sign test cannot establish mean effect >=10pp; seed power q=.7/.8/.9 hypothetical only.

**R4 — AM04: integer category gates (PASS in V3 only):** Check 308,39,192 thresholds; 4/4 nonnegative category and 3/4 >=5pp; skeleton-specific heterogeneity and label/cue shortcut diagnostics with no posthoc hidden success thresholds; explain no claim all 16 skeletons benefit.

**R5 — AM05: gold-adjacent AST security (CRITICAL):** Challenge explicit TRUSTED auditor allowed to read EVAL AST that might encode gold, while owner cannot. Does a single sealed audit eliminate adaptive oracle risk? Can receipt PASS/FAIL/UNKNOWN+hashes/signature leak information through retries or different batch commitments? Are signer keys, ACL, logs, private witness, custodians and threats specified sufficiently for a design GO? Actual ACL/signature/rights still `NOT_VERIFIED`.

**R6 — AM06: contrastive package causal estimand (HIGH):** V4 deliberately relabels B-v-C as **loss + negative-supervision + extra compute package effect**, not loss-only. Test whether hypothesis/metrics/labels are fully consistent; ensure no hidden objective-only claims, no EVAL negatives, source provenance, ratios, coefficients, LR, RNG roots, AdamW resume, T4 budget and one-shot fail-closed are prospective gates. No fourth control arm, planned 36 arm-runs/9216 steps/18432 outputs; no free T4 capability demonstrated. Consider what can actually be concluded if C wins.

## 3. Do not conflate three kinds of PASS

`V4_SELF_AUTHORED_QA=44/44 assertions and 15/15 deliberate JSON mutations` checks *contract presence/consistency only*. It cannot validate real AST semantics, parser false positives/negatives, gold security, stochastic seed independence or Free T4 availability.

Design review `GO_DESIGN_ONLY` (if warranted) allows later implementation/source-QA planning **not** science dispatch. Actual future integrated preexec gate must prove code/rights/ACL/resources/resume before any owner science authorization.

## 4. Deliverables and adjudication

Create:
1. `TTM_D1_BRIDGE_V4_DISTINCT_INDEPENDENT_SOURCE_REVIEW_20261114.md`
2. `TTM_D1_BRIDGE_V4_DISTINCT_INDEPENDENT_REVIEW_RECEIPT_20261114.json`

Each should include the 7 exact source pins, R1–R6 PASS/HOLD/FAIL, severity and source-pointer per finding, original 17 issue coverage and any additional V4 findings, arithmetic audit, the independence classification `INDEPENDENT_NEW_CHAT_AI_SELF_ATTESTED`, and a **single** verdict for design:

`GO_DESIGN_ONLY` / `HOLD_REVISE_BEFORE_PREREG` / `FAIL_INVALID_DESIGN` / `HOLD_SOURCE_UNAVAILABLE`.

If HOLD, suggest **one** integrated next amendment (V5 only), not editing V4 or micro-permits. If GO_DESIGN_ONLY, specify actual implementation/source tests required before science; it is not permission to GPU. If source unavailable, say so rather than infer.

Preserve all: `D1_BRIDGE_SCIENCE=HOLD`, `D1_EXISTING=HOLD_UNMODIFIED`, `TEST_Q1Q2=SEALED`, `FC01_EXPLORATORY=CLOSED_PASS_SCOPED`, `FC02=NOT_OPENED`, `GPU=NO`, `TRAIN=NO`, `INFERENCE=NO`, `MAIN=UNCHANGED`, `V1/V2/V3/V4=IMMUTABLE`. Do not access private gold, train, run models or read sealed mappings. No rerun of FC01.

**Bắt đầu đọc nguồn và review ngay**; không cần micro-acceptance. End with one **Bước thực hiện tiếp theo**.
