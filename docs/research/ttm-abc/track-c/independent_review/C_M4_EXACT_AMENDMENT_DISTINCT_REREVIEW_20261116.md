# Agent C — M4 exact-amendment distinct re-review (2026-11-16)

**Operation:** \`C_M4_EXACT_AMENDMENT_DISTINCT_REREVIEW_SINGLE_GATE\`  
**Verdict:** **PASS_DESIGN_SCOPED** (C-F01 and C-F02 closed for *toy/design contract*; not an SFT integration/science approval)  
**Reviewed exact source HEAD:** \`185d465c31f5f4bef6220be95e39dac1ae81c5b8\` · [Draft PR #35](https://github.com/minhtri22/TokenToModel-Lab/pull/35)  
**Prior reviewed source:** \`8e0a1880e564e92d017847e9f18e53e42b7353c8\` · [prior distinct HOLD_DESIGN report](https://github.com/minhtri22/TokenToModel-Lab/blob/98af7af0632ba38f1b9747cd784964257e39cf16/docs/research/ttm-abc/track-c/independent_review/C_M4_INDEPENDENT_DESIGN_REVIEW_20261116.md)  
**Review branch:** \`review/ttm-track-c-m4-amendment-rereview-20261116\`; branched from exact C amendment HEAD. No change to Agent C's branch, earlier reviewer branch, \`main\` or \`lineage.md\`.

## Scope and byte custody

GitHub readback confirmed PR #35 **Open / Draft** at exact reviewed HEAD. Compared old \`8e0a1880\` to new \`185d465c\`: one commit ahead with **seven** changed paths, all within Track C contract/tests/receipt/status/config/handoff. No edits to Track A/B or science artifacts in that amendment.

Independently reconstructed the exact Python test inputs from GitHub connector and verified **both raw SHA-256 and Git blob SHA-1**:

| Input | Git blob SHA-1 | SHA-256 |
|---|---|---|
| \`tests/ttm_track_c/synthetic_contract.py\` | \`83c6d5abe0948c24c9e49375ffc2a17e3143a793\` | \`522618430f32fd0cc74da945a7bf208aad3a146c1f113a320a13e9490f9e2b88\` |
| \`tests/ttm_track_c/test_synthetic_contract.py\` | \`0681c0fd6550675baa011de78d2590fc27ba604f\` | \`cb679b84900c6241e462487e61320483f6d0b5e79fbb4ed59550fda2200d8abd\` |
| \`tests/ttm_track_c/test_amendment_negative.py\` | \`30c3ddbdbcf907d5d16ca9247c1f683d26d26150\` | \`f89f86dffaf61e92eb016f1d8fcf5b4a2075c24e4ab7f53af24413f5b08e11d4\` |
| \`reviewer_red_contract_checks.py\` from prior independent review @ \`98af7af\` | \`12deb46873a592bdb12cc0ca01908e0cd7c12788\` | \`806faf955c6d37226d8ddaf8876edbff8e181fd1d2d5c853ec0d88124cde4b1f\` |

The additional distinct reviewer test source \`docs/research/ttm-abc/track-c/independent_review/test_distinct_rereview.py\` is committed on **this** review branch, Git blob \`da2f1136fe940e6ef8559bf14fbdef811422babf\`, SHA-256 \`3daf012060254649255385f6a009bde958396079f5d86bbd49cf50c6039945fd\`; exact source readback matched the locally executed byte image.

## Independent native execution (synthetic only)

CPython **3.13.5 Linux x86_64**, standard library, no model, Torch, tokenizer, GPU, real source data or private checkpoint:

| Suite | Independent result |
|---|---:|
| Original tests, exact byte-pinned | **14/14 PASS** |
| Agent C amendment tests, exact byte-pinned | **10/10 PASS** |
| **New reviewer-authored** adversarial tests | **9/9 PASS** |
| Prior reviewer red tests, exact byte-pinned | **2/2 PASS** |
| **Total** | **35/35 PASS** |

Independent added tests include an oracle **derived from roles rather than implementation flags** over **5,000 independently seeded multi-turn conversations** (seed \`913577\`), every flag-bit inversion in a representative system/user/assistant dialogue, user/assistant supervision count conservation attacks, reserved special-token injection, minimal length and EOS boundary, NFC/NFD+casefold, and acknowledgement that self-consistent forged roles **cannot authenticate a real corpus**.

**Execution/receipt hashes:** 33-test combined log SHA-256 \`8eac184f6a0d0beff434f31cd2e9cef1bcbacd53d6ed8ad7656490e667c3418b\`; two red-test log SHA-256 \`bf87aa39d6b5d5ce79a23ff205ea12c7dad7b8e570e35a299a4563d133f67eb8\`. Logs were produced in the independent working sandbox; only the receipt and re-runnable reviewer source are committed, not the full ephemeral logs.

**Test transparency:** The first draft of the reviewer-only injection test had one false failure because it asked for an exception when replacing an EOT with the **identical EOT** at its own position (a no-op). I corrected only that invalid reviewer-test assumption, not Agent C's source, then reran the entire suite: **33/33 + 2/2 PASS**. This failed *test hypothesis* is not a source blocker, and is disclosed rather than erased from the review narrative.

## Adjudication

**C-F01 — PASS_DESIGN.** \`C_SFT_PROTOCOL.md\` now distinguishes **zero direct per-position prompt-target CE weight** at \`ignore_index=-100\` from gradients flowing through prompt embeddings and attention due to assistant-target loss. The specified test no longer demands \`dL/d(prompt_embedding)=0\`. Tests affirm the +1 shift and user/system/header/pad exclusion. The scalar chain-rule example is explanatory, **not** a neural-network gradient measurement.

**C-F02 — PASS_DESIGN.** \`shifted_padded_targets\` reconstructs mask from complete toy-role serialization and compares every supplied flag. The previous reviewer counterexample (\`flags[2]=1\` for a user token) now raises; bit inversions, malformed structural IDs, wrong EOT and loss target suppression fail. The proposed B-facing \`build_sft_targets(messages,max_len)\` derives flags internally. It does **not** certify caller-authored roles, source provenance, tokenizer or rights. This is properly disclosed, so it is a design-scoped PASS rather than B production admission.

**C-F03 — PASS_ADVISORY_SCOPED.** Canonical NFC+casefold+whitespace normalization catches canonical-equivalent cross-split toy duplicate rows. Exact byte hash remains distinct; real near-dup/family analysis remains unimplemented.

**C-F04/F05 — unchanged limitations.** The five-level gold/rater rubric is unvalidated on real controlled outcomes; equal target exposures have not established measured compute parity. Neither was an original blocking scope item for the synthetic mask correction.

### Gates after this re-review

| Gate | Adjudicated state |
|---|---|
| C-G0 | \`PASS_SOURCE_INVENTORY_SCOPED\` |
| C-G1 | \`HOLD_REAL_DATA_UNAVAILABLE\` |
| C-G2 | \`DESIGN_VALIDITY_UNPROVEN\` |
| C-G3 | \`DESIGN_ONLY\` |
| C-G4 | \`WAIT_A_B\` |
| **C-G5** | **\`PASS_DESIGN_SCOPED_B_INTEGRATION_NOT_EXECUTED\`** |
| C-G6 | \`DESIGN_ONLY\` |
| C-G7 | \`NOT_AUTHORIZED\` |
| C-G8 | \`NOT_EXECUTED\` |

**Overall:** \`PASS_DESIGN_SCOPED\` supersedes the **prior design decision for the two corrected contract findings** without rewriting its historical report. PR #35 remains Draft / unmerged. Track B may develop its GPT Core independently but must not treat the toy API as *native B integration PASS*. No training, SFT, model forward, TEST consumption, GPU, merge or owner science GO.

**Independence caveat:** the design assessment, new oracle and new adversarial tests were authored in a different ChatGPT reviewer session from Agent C, but published via the linked owner's GitHub account; do not imply a separately authenticated human reviewer.

## Reproduction

On the review branch, set \`PYTHONPATH=tests/ttm_track_c\` and run:

1. \`python -S -B -m unittest discover -s tests/ttm_track_c -p "test_*.py" -v\` — 24 author tests, independently rerunnable.
2. \`python -S -B -m unittest discover -s docs/research/ttm-abc/track-c/independent_review -p "test_distinct_rereview.py" -v\` — 9 distinct reviewer tests.
3. Fetch exact prior red test from pinned reviewer commit \`98af7af0632ba38f1b9747cd784964257e39cf16\` to a separate temporary directory and run it with the same \`PYTHONPATH\`: \`python -S -B reviewer_red_contract_checks.py -v\` — 2 tests.

Windows Python 3.12 was **not** executed by this reviewer; tests are pure Python stdlib.

**Bước thực hiện tiếp theo — duy nhất:** \`C_M4_PASS_DESIGN_HANDOFF_TO_PM_B_INTERFACE_QUALIFICATION_SINGLE_GATE\`. PM records the design-scoped verdict and coordinates **one integrated B-facing interface qualification** (real tokenizer ID map/chat template, masked CE+shift, attention/padding, versioned hashes, synthetic CPU forward/negative QA). Treat B integration, rights, gold, science and merge as separately unqualified; no micro-permits or science dispatch.

