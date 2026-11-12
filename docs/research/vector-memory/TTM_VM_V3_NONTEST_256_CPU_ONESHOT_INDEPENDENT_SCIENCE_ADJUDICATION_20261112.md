# TTM Vector Memory V3 — Phân xử độc lập NON-TEST 256, AI-amended

**Operation:** `TTM_VM_V3_NONTEST_256_ONE_SHOT_RESULT_INDEPENDENT_RECOMPUTATION_AND_ADJUDICATION`  
**Ngày:** 2026-11-12. **Classification:** `AI_ASSISTED_EXPLORATORY_SCOPED`.  
**Run ID:** `TTM_VM_V3_NONTEST_256_FROZEN_READER_CPU_ONESHOT_V1`.  
**Runner science verdict:** `GO_CANDIDATE_NONTEST_AMBIGUITY_SCOPED`.  
**Independent adjudication:** **`PASS_NONTEST_V3_SYNTHETIC_AMBIGUITY_EXPLORATORY_SCOPED`**. Không phải TEST PASS, không phải thành công của learned vector/semantic retrieval ngoài domain.

## 1. Giới hạn nguồn, custody và một lượt CPU

- Science source commit **`e258f117d0422e2e83d9cf5937aad889f187a2bf`**, runner source Git blob `32e2a15ba56916958102294efe4d91c4fbc812e4`; V3 fixture generator blob `5f51b8b464e54a370f3a3fa99d91307118f52f46`; V3 deterministic rule Retriever blob `68bfeaaf1d0acf0cf446e4d734e34368fbf8f702`.
- V3 owner-private fixture 256 cases SHA256 `d473292d40dfb475d0b44f7d393341e19d846308820dcb4f5cbac6acb2c0e543`. Pinned L0020 trained Reader SHA256 `c458de3afae87b3c381274b8edd698187df63ceac4dbbc0e6d8bd44b85c1632f`. P02 GPT SHA256 `ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc`; T1 manifest SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- Owner native pre-exec sources `SOURCE_QA=99/99`, scorer `MOCK_QA=100/100`, Reader/backbone/fixture/T1 SHA PASS, AI P1 `32/32` each and gold matches. Human-review requirement was **not met**. Owner expressly approved the prospective-to-CPU amendment `docs/research/vector-memory/TTM_VM_V3_AI_SUBSTITUTION_PROSPECTIVE_AMENDMENT_20261112.md` after seeing AI outputs but before science. This is **AI-assisted exploratory** and may be biased by this chronology, not a human-independent review.
- Windows owner one-shot marker and results in `D:\WORK\RESEARCH\TokenToModel-Lab\_evidence\vector-memory\TTM_VM_V3_NONTEST_256_FROZEN_READER_CPU_ONESHOT_V1\`: `ONE_SHOT_STARTED.json`, `PER_STORY_QA_PRIVATE.json`, `PROBE_AGGREGATE_PUBLIC.json`. **ONE_SHOT=CONSUMED**, never rerun. Reader/weights reported unchanged; optimizer steps 0, GPU unused, TEST sealed, no old PROBE or DEV rescore.
- Owner raw public aggregate SHA256: **`579f9a568196d9ab704a4fdfaedb8e12ed08b80c6c4ffc9bb8acc26409538dd8`**. Independent readback of text from Windows reconstructed **CRLF with final CRLF** and obtained exact same SHA256. This validates the text representation against native digest, **not an independent raw binary stream**.
- All **256/256 per-story records** (4,994 text lines) read directly via owner Windows read-only connector. Public aggregate-only QA receipt `artifacts/research/vector-memory/TTM_VM_V3_NONTEST_256_CPU_ONESHOT_INDEPENDENT_PERSTORY_QA_AND_ADJUDICATION_20261112.json`; private per-story data never uploaded to GitHub.

## 2. Retrieval action and abstention (pre-registered fixed denominators)

| Stratum | Cases | Correct action | Correct |
|---|---:|---|---:|
| P0 KNOWN_WIRING, engineering control | 32 | `SELECT` | 32/32 |
| **P1 UNSEEN_PARAPHRASE, primary** | 32 | `SELECT` | **32/32** |
| **P2 PROVENANCE_UNIQUE, primary** | 32 | `SELECT` | **32/32** |
| **P3 NEGATION_UNIQUE, primary** | 32 | `SELECT` | **32/32** |
| **N0 UNDERSPECIFIED, primary** | 32 | `ABSTAIN` | **32/32** |
| **N1 DUPLICATE_MATCH, primary** | 32 | `ABSTAIN` | **32/32** |
| **N2 CONTRADICTORY_QUERY, primary** | 32 | `ABSTAIN` | **32/32** |
| **N3 UNRESOLVABLE_OOV_OR_EXCLUSION, primary** | 32 | `ABSTAIN` | **32/32** |

- Primary positive `CorrectSelectRate=96/96=1.000` (pre-frozen ≥72/96=0.75). P1 `32/32` (≥20/32). Wilson 95% positive proportion CI `[0.9615244121;1.0000]`.
- Primary negative `CorrectAbstainRate=128/128=1.000` (pre-frozen ≥122/128=0.95), **0 false selections/128** (≤6). Wilson 95% negative proportion CI `[0.9708630437;1.0000]`.
- N0/N1: 64 `MULTIPLE_PUBLIC_MATCHES`. N2: 32 `CONTRADICTORY_POSITIVE_NEGATIVE_CONSTRAINT`. N3: 16 unsupported OOV material and 16 contradictions. **All 128 negatives have `nll=null` and `reader_forward_calls=0`**, so abstention is not improperly evaluated with fabricated Reader answers. Diagnostics cost `3×false_negative_select + 1×missed_positive =0`.
- P0 32 is engineering only, **excluded** from primary 96. No denominator alteration, no filtering abstentions after scoring.

## 3. Frozen Reader — primary 96 positive stories

Answer-only mean **per-story NLL** (nats/token; lower is better). **300 answer tokens** in each arm across the 96 stories.

| Arm | Mean per-story NLL |
|---|---:|
| A — no memory | `6.982178146640460` |
| O1 — gold Oracle singleton (control, not real Retriever) | `3.925246059894562` |
| B1 — selected correct-memory singleton | `3.925246059894562` |
| C1 — same selected key, target value swapped | `5.378724733988444` |
| B3 / C3 diagnostics | `3.925246059894562` / `5.378724733988444` |

**B3/C3 are deliberately identical to B1/C1 for a singleton selected card. They are NOT an independent Top-3 experiment**; these must not be reported as novel Top-k efficacy.

**Pre-frozen positive gates:**

| Gate | Threshold | Computed |
|---|---:|---:|
| Mean paired `NLL(A)−NLL(B1)` | ≥0.05 | **+3.056932086745898 PASS** |
| Mean paired `NLL(C1)−NLL(B1)` | ≥0.05 | **+1.453478674093882 PASS** |
| Oracle positive control `NLL(A)−NLL(O1)` | ≥0.05 | **+3.056932086745898 PASS** |
| Both paired-bootstrap percentile 95% lower bounds | >0 | **PASS** |

Runner NumPy PCG64, 2,000 paired bootstrap replicates (seeds `20261120`/`20261121`):
- `A−B1`: **[2.8170127306754393; 3.321249547662834]**
- `C1−B1`: **[0.8661692519361773; 2.0791262958819665]**

Auditor independently resampled **the same 96 per-story difference vectors** with Mulberry32 (different PRNG, 2,000 draws, same seed identifiers):
- `A−B1`: **[2.815340967910985; 3.320688444872697]**
- `C1−B1`: **[0.8929001674676935; 2.1098398956159747]**

The two independent percentile interval pairs overlap closely and their lower bounds are positive. The resampling sequences are intentionally different; exact endpoint equality is not expected. **B1 and O1 have bit-exact NLL equality on all 128 positive stories**, reinforcing the conditional equivalence of retrieved singleton and Oracle in this synthetic dataset.

## 4. Read-only independent QA 73/73

Auditor read marker, 256 private per-story outcome records and public aggregate. Recomputed all eight strata counts/reason codes; unique case IDs; correct/abstain rate, Wilson CI, total answer token count, 96-story six-arm means, two paired deltas, Oracle delta, independent paired-bootstrap confidence intervals and pre-frozen gate precedence; examined source code proving Retriever only sees `question`+`public_index`, while `hit1` is derived after retrieval by comparing selected index to private `target_key` and no-model `action_only` handles negatives.

- **73/73 checks PASS**. One earlier check incorrectly used JSON string equality for `reason_counts` across object insertion orders and appeared FAIL. It was **an auditor QA bug**, not source/data disagreement. Replacement check compared unordered reason-to-count maps over all 8 strata; **8/8 PASS**, and repeated 10/10 critical safeguards. No data, seed, runner or scientific result was changed.
- The per-story output does **not** include each selected key/index, only `hit1/correct_select/status/selected_count`. Thus the audit recomputed outcomes from **logged correctness flags**, and cross-inspected the pinned source path that derives them from private gold; the auditor could not independently compare every selected index to its private gold using the logged per-story file alone. Distinguish this qualified read-only QA from a fully external raw-trace attestation.
- No independent post-run SHA rehash of private Reader binary/checkpoint was performed. The owner preflight and pinned runner verified pre-run SHA and reported unchanged state; this remains an evidentiary limit.

## 5. Phán quyết khoa học có giới hạn

**`PASS_NONTEST_V3_SYNTHETIC_AMBIGUITY_EXPLORATORY_SCOPED`**, matching the previously frozen V3 screening thresholds after the explicitly documented owner AI-custody amendment. It establishes that a **deterministic symbolic Retriever** with the frozen published grammar, source constraints, negation and explicit abstention behaves correctly on the **same family of synthetic generated cases**, and that a previously trained frozen Reader improves answer-only NLL when given a correct singleton.

**It does NOT establish:** open-ended semantic retrieval, learned vector retrieval, out-of-grammar unseen paraphrase generalization, robust real-world calibrated uncertainty, real evidence provenance, natural language ambiguity at scale, true Top-3 RAG, heldout TEST, or general superiority to the old V2 baseline. P1 phrases are **unseen relative to V2 but already present in V3's frozen lexicon**; their 32/32 pass must not be called "unseen to this Retriever." The V2 success remains scoped; **L0021 cosine FAIL is not negated**.

The 256 V3 NON-TEST PROBE cases are **now consumed**. They may not be reused as new-heldout evidence after any tuning or algorithm change. Do not rerun one-shot, unseal TEST, retrain Reader or modify old lineage entries.

## 6. Next scientific operation

**`TTM_VM_V4_NATURAL_LANGUAGE_OOD_AMBIGUITY_UNSEEN_RELATIONS_PREREG_DESIGN_ONLY`**: design a fresh genuinely out-of-grammar, independently annotated, hard-negative dataset with different templates and data provenance, explicit optional abstention and fair frozen lexical/embedding baselines before any execution. Prioritize data sources/independence and negative safety; preserve `TEST=SEALED` and `GPU=NO`.

**Durable status:** `V3_SCIENCE=PASS_NONTEST_EXPLORATORY_SCOPED` · `AUDITOR_QA=PASS_73_OF_73` · `ONE_SHOT=CONSUMED` · `AI_ASSISTED_REVIEW=DISCLOSED` · `TEST=SEALED` · `MAIN=UNCHANGED` · `LINEAGE=APPEND_L0023_ONLY`.
