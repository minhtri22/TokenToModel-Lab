# Track A M0 — adversarial QA and single I1 adjudication

**Operation:** `A_M0_GOLD_BLIND_SCORER_FIX_SPLIT_LEAK_NEGATIVES_AND_SINGLE_I1_REVIEW`  
**Decision:** **`HOLD_I1`** · **blocker:** `NEW_PROTOCOL_NOT_END_TO_END_ADMITTED`  
**Date:** 2026-11-16 · **Scope:** source, MOCK, Windows Python 3.12 + Windows PowerShell 5.1 compatibility. **No model science.**

## Evidence read and exact pins

- Handoff A at `892594577aa45f3b07be577103dd2355de8cf7dd`; stacked PR #33 exact base `ebdc54575eed1ff60c402eecf60289f408bb38ca` (PR #28).
- Legacy Q001 scorer at `6dc04c0545b28d4a0cad21ad8be8b70461c57790`; historical verdict `HOLD_I1_RESTRICTED_SCORER_LABEL_LEAKAGE`; historical fixture SHA-256 `5f1234f583ccf719ca9f0e68de4f47d8b653af777271b8115c5f02307f764e5a`, **immutable**.
- Final reviewed source state: `94eeaf93a24af6cf579a150bc2af62ce603723c3`; source SHA-256: scorer `98101e871410e7255cd25f611e5eb9d7068ab264ac162e0af89ef1f1863f6587`, adversarial suite `90d4050d52c0bf2146f5ea4fb7af55acbbc33dfa486ada25b7ad5846344b293b`, alternate checker `e14fb012eff259452555bf598131398b06f962ce8997566ca6416a536d8edcd2`.
- CI [Windows 2022 / Python 3.12 QA](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43891380753), job `133383186868`, concluded **SUCCESS**. Windows PowerShell 5.1 mock compatibility step PASS; other steps used PowerShell 7.
- [M0 mock manifest](M0_V3_MOCK_FIXTURE_MANIFEST_20261116.json) pins 80 case hashes, 5 group hashes, and fixture SHA-256 `f696d20af567ba52dbb9187aba87092829b4da7f3974fbe062608659bd99e726`. This is a **new public mock fixture**, not real-token I1 custody.

## Adversarial technical results

| Control / gate | Observed result | Meaning |
|---|---|---|
| Author mock source checks | **10/10 PASS** | Determinism, counts, no binding leak, ties abstain |
| Python 3.12 unittest adversarial negatives | **16/16 PASS** | Tampered gold, shuffled choices, queried-key swap, parent and held-out leakage, unseen random candidate pool, full-vocab divergence |
| Alternative algorithmic checker | **PASS_MOCK_LOGIC; 0 findings** | Independently coded oracle, candidate reconstruction, binding audit and constant-logit check |
| Constant equal logits | **0/80 candidate-only; 0/80 full-vocabulary** | Both abstain rather than exploiting first listed choice |
| Blind fixed token-ID ranking | TRAIN **4/24**, RECOMBINED **8/16**, NOVEL_IDS **1/16**, PAIRED **9/16**, ABSENT **0/8** candidate-only | Fixed logits use no context; illustrates residual chance/ID bias, not model capability |
| TRAIN binding repetition in independent holdouts | **0** | RECOMBINED and ABSENT exclude both TRAIN bindings |
| Counterfactual parent relationship | **16/16 explicitly linked** | Not independent of TRAIN; no inflated sample count |
| Novel key/value token overlap with TRAIN | **0** | Applies to key/value IDs; grammar/role tokens intentionally shared |
| Legacy four-choice negative | constant logits **80/80** (historical result) | Invalid legacy score, not a rerun or proof about a model |

**Limitations of the alternate checker:** It is written separately from the main scorer but authored and invoked under the **same Agent A session/account**. It does **not** constitute a truly distinct independent reviewer under the Handoff A acceptance rule. It only provides algorithmic cross-checking. The CI workflow is also a technical mock QA, not the original native release-runner/Win32 Job Object suite.

## I1 verdict and non-fabrication

**`HOLD_I1`**. The single governing blocker is **the amended v3 measurement protocol is not end-to-end admitted**:

1. A new *mock-only* scorer and deterministic 80-record fixture exist, but the legacy original one-shot runner still contains `opts=[gold]` and its historical 80-record fixture semantics. No verified v3 fixture is frozen from the private, pinned actual tokenizer inventory, and no guarded release runner consumes v3.
2. The required genuinely distinct independent reviewer has not verified amended scorer + fixture + runner together at their exact source pins.
3. No new science threshold/one-shot release is established for this materially amended protocol. Owner's preexisting conditional GO cannot be silently transferred to a new fixture/protocol.

These are **one integrated I1 admission problem**, not requests for separate micro-permits. The mock fix is useful and CI-backed; it does not erase historical QA or confer scientific validity. Existing 16/16 native Win32 Windows QA/checkpoint SHA are inherited **without rerunning or changing them**; no private checkpoint was loaded in this operation.

| Gate | Verdict |
|---|---|
| A0 exact source/base diff and historical negative | `PASS_SCOPED` |
| A1 new mock metric / negative QA | `PASS_MOCK_ONLY`; **overall A1 HOLD** pending end-to-end source |
| A2 Python 3.12 + PS 5.1 compatible mock QA | `PASS_SCOPED` (original guarded runtime not re-executed) |
| A3 prospective scientific method | `DESIGN_ONLY` |
| A4 scientific execution | `NOT_EXECUTED` |
| A5 independent I1 adjudication | `HOLD_I1` (distinct reviewer missing) |

**No I2**, optimizer steps **0**, model forwards **0**, no newly claimed nonce, no repeated historical TEST/FRESH16/FINAL24/EXP32, no change to old science, `main`, PR #28 source, `lineage.md`, Track B/C or private checkpoint. PR #33 remains DRAFT, do not merge.

## Bước thực hiện tiếp theo — duy nhất

`A_M0_V3_INTEGRATED_REAL_FIXTURE_RUNNER_CUSTODY_NATIVE_AND_DISTINCT_I1_ADJUDICATION_SINGLE_GATE`

Trong **một lượt tích hợp**, đưa v3 vào đường runner bị khóa, đóng băng fixture **mới** bằng inventory thật với SHA/parent/split manifest, làm đúng QA native cho mã vừa thay đổi, rồi giao một reviewer **khác Agent A** phân xử exact HEAD. Nếu tất cả đạt mới `I1_PASS`; nếu không giữ `HOLD_I1`. **Không chạy I2 trong lượt này.**
