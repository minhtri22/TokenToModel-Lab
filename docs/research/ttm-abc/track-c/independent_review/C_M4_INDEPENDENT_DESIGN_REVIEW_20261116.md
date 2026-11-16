# TTM Track C — M4 Independent Design & Synthetic Contract Review

**Review operation:** `C_M4_INDEPENDENT_DESIGN_AND_SYNTHETIC_CONTRACT_REVIEW_SINGLE_GATE`  
**Review date:** 2026-11-16 · **Verdict:** **`HOLD_DESIGN`** (two scoped design/interface blockers; not a rejection of the whole research direction)  
**Reviewed exact source HEAD:** `8e0a1880e564e92d017847e9f18e53e42b7353c8` · PR [#35](https://github.com/minhtri22/TokenToModel-Lab/pull/35)  
**Comparison base:** `666bc2c95ba21eaddcf8a0e3f8ed7cd906629de2` for M4 additions; `main=f7a0a5874e8fd895c8ea8d17ceff393a4d4917a3` for PR baseline.  
**Reviewer:** independent source/design assessment in separate ChatGPT PM session, not author Agent C; GitHub authorization may be the same owner account and is not evidence of different human identities.  
**Evidence branch:** `review/ttm-track-c-m4-independent-design-20261116` (initial parent = reviewed exact C HEAD; no changes to agent C branch, main, or prior evidence).  
**Execution scope:** Python 3.13.5 (Linux x86_64) stdlib synthetic-only; no Windows Python3.12; no torch, model forward, real data, training, GPU, SFT, checkpoint or independent AI rater.

## 1. Byte/readback and independent reproduction

Inspected all 10 changed PR #35 files. Source code and original author test bytes independently reconstructed from exact GitHub fetch and verified against author receipt's SHA-256:

| File | Git blob SHA-1 | SHA-256 verified independently |
|---|---|---|
| `tests/ttm_track_c/synthetic_contract.py` | `9e9fdd8fea0baec92c82be4caecbd71f32f66fc4` | `ab649f978c4521da8402238b0d76c65e5ec349e441f3fef3de8a9fdee8bd58cc` |
| `tests/ttm_track_c/test_synthetic_contract.py` | `0681c0fd6550675baa011de78d2590fc27ba604f` | `cb679b84900c6241e462487e61320483f6d0b5e79fbb4ed59550fda2200d8abd` |

Author tests rerun independently from matched bytes:
`python -S -B -m unittest discover -s <read-only-exact-source-directory> -p test_synthetic_contract.py -v`: **14 passed / 14, exit 0**.

Reviewer-added differential/property probes on the matched `synthetic_contract.py`: 1,000 random multi-turn conversations with optional system messages and +1 shift, EOT/EOS counts, reserved-token exclusion, max-length boundary, casefold cross-split collision, manifest order invariance, gold-none abstention, synthetic slot correctness. **11/11 observations reproduced as expected**; two of these demonstrate unsafe/incomplete input behavior rather than successful security controls. The reviewer also authored two explicit **red acceptance tests**: both FAILED on the exact source, as anticipated. The red test source SHA256: `806faf955c6d37226d8ddaf8876edbff8e181fd1d2d5c853ec0d88124cde4b1f`.

No claim is made of full assurance beyond these cases or of verification on user's Windows Python3.12.

## 2. Findings by importance

### C-F01 — BLOCKER: prompt-loss masking versus prompt-gradient semantics

In `docs/research/ttm-abc/track-c/C_SFT_PROTOCOL.md` §4(2), the proposed B-integration acceptance includes *"negative assertions on prompt-gradient contribution."* That is ambiguous in a way that can produce a scientifically wrong SFT test.

Correct property: with `L=-log p_theta(assistant_answer | system,user)`, all system/user/header token **target positions** have no **direct cross-entropy term**. However gradients of the **assistant answer loss** normally flow through prompt embeddings, attention and shared parameters because the answer is conditioned on the prompt. Thus `dL/d(prompt_embedding)` need not be zero. Testing for zero gradient there can reject a correct decoder or suppress conditional learning.

**Required amendment:** replace the phrase with an exact test of direct loss target masking (`ignore_index=-100`, +1 shift, zero direct per-token prompt CE weight, assistant answer/EOT/EOS supervised); explicitly state that gradients through the prompt context are allowed and expected. Add a negative mask-position test. Do not assert all prompt-embedding gradients are zero.

**Status:** `HOLD_DESIGN` until corrected; no need for new owner science permit.

### C-F02 — BLOCKER: untrusted caller-supplied flags can supervise a user token

`tests/ttm_track_c/synthetic_contract.py` function `shifted_padded_targets(ids,flags,max_len)` validates bit values but NOT their derivation from an authenticated `serialize(messages,...)` result. A concrete reviewer counterexample:

```python
ids, flags = serialize([
    {"role":"user","content":[77]},
    {"role":"assistant","content":[88]}
], 12)
flags[2] = 1  # user content token at index 2
x, y = shifted_padded_targets(ids, flags, 12)
assert 77 in y  # observed: accepted, user becomes a supervised target
```

This **does not mean the normal `serialize → shifted_padded_targets` path leaks**; it does not, as original QA and independent property tests showed. The missing protection is at the **B integration boundary** when masks are passed separately. Either bind derivation internally/validate against role structure, or explicitly make the low-level function trusted-internal only and add a public wrapper/integration negative test that rejects mutated mask provenance. Preserve complete transcript/attention semantics.

**Required amendment:** document the invariant, implement a verifiable B-facing boundary and include reviewer counterexample as a negative test. `HOLD_DESIGN` on the interface until fixed.

### C-F03 — ADVISORY: 'normalized' duplicate signal lacks Unicode canonical normalization

The toy `audit_toy_records()` uses `casefold + whitespace collapse` but no Unicode NFC/NFKC. Thus `é` (U+00E9) in TRAIN and `e\u0301` in VAL yield `cross_split_normalized_groups=0`. The reviewer red expectation of 1 fails. This is **not** proof of real T4 leakage and **not** a blocker for a clearly toy-only audit (the document openly says near-duplicate detection is not implemented). Before real C-G1, specify canonical Unicode normalization, language-specific equivalence, near duplicates and source-family grouping; never promote toy collision counts to production claims.

### C-F04 — SCOPE LIMITATION: gold/rubric is an uncalibrated design

`C_EVAL_CONSTRUCT_AND_DATA_AUDIT.md` correctly separates gold from model outputs and specifies K0–K4, false-positive fluent-wrong, oracle, ceiling/floor, byte-visible rater provenance and disjoint splits. Yet the 14 tests exercise only `score_slot()` and `floor_state()`, **not** a five-level rubric/rater calibration or blinded gold generation. Therefore `C-G2=DESIGN_PLUS_TOY_QA` only; do not claim an independently validated measurement instrument. Not a design blocker because the current task explicitly excludes actual rater/real model data.

### C-F05 — SCOPE LIMITATION: prospective equal-exposure design is not measured equal-compute

`C_DATA_OBJECTIVE_CAPACITY_MATRIX.md` correctly computes 1,024 × 4,096 = 4,194,304 exposures per arm per seed; 3 arms × 5 proposed seeds = 62,914,560 exposures, 12 total seeds = 150,994,944. The document itself warns equal target exposures ≠ equal FLOPs or wall-clock. Actual tokenizer/source rights, B trainer, GPU time/VRAM and power are unavailable. Keep `C-G3=DESIGN_ONLY` and `C-G7=NOT_AUTHORIZED`. No issue requiring a separate permit now.

## 3. Gate adjudication (scoped, not scientific)

| Gate | Independent review status | Reason |
|---|---|---|
| C-G0 | `PASS_SOURCE_INVENTORY_SCOPED` | Exact PR35 files/diff and matched source bytes verified |
| C-G1 | `HOLD_REAL_DATA_UNAVAILABLE` | No private corpus, real histogram, near-dup, split/group SHA, action-specific rights |
| C-G2 | `DESIGN_VALIDITY_UNPROVEN` | Gold/rubric documented, toy only, no independent full calibration |
| C-G3 | `DESIGN_ONLY` | Arm matrix, exposure arithmetic valid, no measured compute or preregistered science |
| C-G4 | `WAIT_A_B` | Qualified Track A endpoint and Track B integrated trainer not established here |
| C-G5 | `HOLD_DESIGN_INTERFACE` | Direct-mask vs gradient wording and mask-provenance gap despite 14/14 |
| C-G6 | `DESIGN_ONLY` | Architecture ideas not independently benchmarked |
| C-G7 | `NOT_AUTHORIZED` | Resource/owner science decision absent |
| C-G8 | `NOT_EXECUTED` | No model forward, training, SFT, GPU, new science |

**Overall design verdict:** `HOLD_DESIGN` on **C-F01 and C-F02**, not on unrelated data-science access restrictions. Existing author `PASS_14_OF_14` remains valid for its scoped fixtures. No merge of PR #35.

## 4. Single remediation and re-review

**Only next operation:** `C_M4_SINGLE_AMENDMENT_SFT_MASK_GRADIENT_SEMANTICS_AND_PROVENANCE_NEGATIVE_QA`.

One consolidated Agent C update to PR #35: (a) correct the direct-loss-vs-context-gradient wording, (b) define/guard flag provenance at B-facing interface, add mutated flag negative test, (c) document Unicode canonicalization limitation explicitly (optional code improvement), (d) update author tests/status/receipts and provide exact new HEAD. A distinct reviewer then rechecks **only affected contracts plus necessary regressions** and returns `PASS_DESIGN` or `HOLD_DESIGN`. Do not request a new GPU/training permit or rerun all previously passing, unchanged tests without reason.

**Independent review does NOT:** amend Agent C branch, open real files, authorize SFT, merge, alter `main` or `lineage.md`, or claim science results.
