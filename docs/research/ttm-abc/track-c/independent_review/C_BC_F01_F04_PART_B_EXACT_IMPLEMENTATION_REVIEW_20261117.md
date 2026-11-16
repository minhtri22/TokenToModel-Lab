# TTM Agent C — PR #36 B–C F01–F04 Exact Integration Review and Scoped Compatibility Verdict

**Operation:** `TTM_PM_BC_F01_F04_WIRE_SCHEMA_HASH_BRIDGE_INTEGRATED_AMENDMENT_AND_DISTINCT_QA_SINGLE_GATE`  
**Reviewer:** Agent C, contract owner and technical reviewer separate from B author; **NOT** the final distinct third-party adjudicator.  
**Date:** 2026-11-17 (local)  
**C verdict:** **`C_CONTRACT_COMPATIBILITY_PASS_SCOPED`** for B v2 synthetic source/CPU path.  
**Program BC-5 verdict:** **`HOLD_DISTINCT_INDEPENDENT_QA_AND_PM_ADJUDICATION`**; no science or merge.

## Exact source and execution custody

- PM handoff: `40788f557799c7c8a688df32271510aab73a9180`.
- B v1 author baseline: [PR #36 at `5f2b71c5f493405c180d6995a21dd7373bd2dbb2`](https://github.com/minhtri22/TokenToModel-Lab/commit/5f2b71c5f493405c180d6995a21dd7373bd2dbb2), implementation v1 blob `636a7d695e49802e3d8d80ab0ef06f25ef7d8322`; B preexisting 29/29 Windows/Linux CI run 43908305162 preserved.
- **B v2 actual reviewed source/test:** `724f62a025b8ecc7c452b9ee16c926adfd2b8c7e`; `src/ttm_track_b/bc_sft_bridge_v2.py` Git blob **`f2cc02821efa4f9628964657d90c7a98c4d67e13`**; B v2 tests `tests/test_bc_sft_bridge_v2.py` blob `cb08038adcceb4848790694b62c97f648d0b1b62`. B own [CI #43918069534](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43918069534) Windows/Linux **SUCCESS**, includes B 29 previous tests, B v2 tests, rerouted exact C18, synthetic P02 forward/backward with zero optimizer, and seven physical artifacts. B baseline other regression [#43918068585](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43918068585) SUCCESS.
- **C prior Part A:** PR #35 source `56c18e2a00714c8a1c118dabc0ede9d2a1b34b17`; C v2 schema-aligned source C HEAD `66c9b92a30cd403aa909528008ffaa6d83286285`, reference oracle blob **`9ae5e8b189b361a496bc7bfd9ec0342bc24a7e72`**. [C source-only CI #43918786173](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43918786173): 18/18 per Windows/Linux Python 3.12 PASS.
- **C implementation test review branch:** `review/ttm-c-bc-f01-f04-20261117`, rooted **exactly** at B `724f62a0...`, with only C 19 tests, exact byte-copied C oracle and workflow. Test Git blob `ccd9b3fdae116a217ef730bf90905cce78de59f0`; copied oracle blob `9ae5e8b189b361a496bc7bfd9ec0342bc24a7e72`. [C review CI #43919831949](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43919831949): Linux Python 3.12.16 **19/19**, Windows Python 3.12 **19/19**, torch 2.10.0 CPU, zero optimizer, both job status SUCCESS. This proves separate C cross-track QA, **not** the final independent reviewer.
- **Transparent failure history:** [C review run #43919542829](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43919542829) FAIL before any tests ran because `python -S` disabled `site-packages` and couldn't import already-installed torch. Review branch changed **only workflow invocation to `python -B`**, not B source or the 19 test bytes; second CI PASS. Do not relabel first run as a source defect or hide failure.
- **B evidence-only continuation:** [`2f1fb24d417cf174804b939c826fa75e94921127`](https://github.com/minhtri22/TokenToModel-Lab/commit/2f1fb24d417cf174804b939c826fa75e94921127) commits the physical canonical LF files; subsequent [B PR #36 evidence HEAD `888acd454d407713a79c02a751c18c8fe009b3e2`](https://github.com/minhtri22/TokenToModel-Lab/commit/888acd454d407713a79c02a751c18c8fe009b3e2) compared to B `724f62a0...` shows **only** `artifacts/ttm-abc/bc-sft/v2/` files and an evidence handoff document, **no `src/` or `tests/` changes**. Avoid treating a later evidence append as new tested implementation without a fresh diff.

## BC-F01–F04 adjudication by C

| Finding | C exact candidate source & native QA | C verdict |
|---|---|---|
| **BC-F01** C string vs B list[int] | B v2 `to_byte_messages` strict UTF-8, byte 0x00, role literal, Vietnamese/emoji, no NFC coercion; reverse rejects invalid UTF-8, original byte-only B path segregated. C's 19 tests independently compare C oracle conversion to B actual conversion and exact `serialize/targets` | **PASS_C_SCOPED** |
| **BC-F02** v1 schema disagreement | Joint v2 identity locked: `ttm.bc.synthetic.sft_pack.v2`, `ttm.bc.synthetic.sft_checkpoint.v2`, `ttm.bc.synthetic.chat_template.v2`, `ttm.bc.c_string_to_b_bytes.v2`. C explicitly agrees to B v2 names; old B/C v1 + C's superseded draft v2 alternative rejected. Despite checkpoint name, `scope=METADATA_ONLY_NO_ACTUAL_CHECKPOINT`, `resume_enabled=false`, weights/optimizer NOT_CREATED | **PASS_C_SCOPED** |
| **BC-F03** canonical JSON LF mismatch | Both C oracle and B v2 encode sorted compact UTF-8 JSON, no Unicode normalization or non-finite numbers, exactly one final LF; B old no-LF v1 historical hashes unchanged. C separately asserts actual bytes equal and rejects LF removal/CRLF mutation | **PASS_C_SCOPED** |
| **BC-F04** seven real artifacts | B `write_bundle` saves physical JSON bytes, reopens them, records SHA; B `verify_bundle` reads bytes independently and semantically recomputes fixture labels/masks. C tests B seven *actual produced files* using **C's own independent `verify_seven_artifacts()`**, mutates each file/hash, forged recomputed target-label digests, schema aliases | **PASS_C_SCOPED** |

### Standalone GitHub byte/readback verification

At B committed evidence `2f1fb24d417cf174804b939c826fa75e94921127`, Agent C fetched `artifacts/ttm-abc/bc-sft/v2/MANIFEST_CANONICAL_LF.json` and seven `actual_bytes/*.json`, then **independently computed SHA-256 from exact UTF-8 GitHub file contents** using a SHA256 implementation self-tested with known `abc` digest. **7/7 exact digests match manifest; all 7 terminal LF PASS; CRLF absent 7/7.** This is not merely seven plausible 64-character strings.

- **Manifest:** Git blob SHA-1 `cba9f094d5d05787ffb50ffdef849049945bbfc8`; SHA-256 `17f91e6d3881404909b6cb8c1cd4a2272a92f8b67c179806c2af68768e86d0a2`.
- `tokenizer_sha256`: `c1d7f880382d28eb099fcae6a620b4587228486d6a1a149cf99dc7bcc527bbf5`.
- `chat_template_sha256`: `6c818dda5ce614483406864bd7289a5131b8e0e2826c732b767afec3aa63b100`.
- `serialized_inputs_sha256`: `03f351b4ddfddaad7fa465ee19e538a9ed199d3602bd772185ac49bc58c2a6e0`.
- `target_masks_sha256`: `4a70ef9b946f1a262dc3210c82098ea3e138ea406ffd4f31bc23d2e82149cc50`.
- `target_labels_sha256`: `9d1a3f3d7f0e910fc318fe6ff5e0353a926d50e45acc278f06cd5b9f610b90cf`.
- `config_sha256`: `c3bd53773db03bb5c86d4279f94453c022d77d198ad49cefe4ab11bbf2420423`.
- `checkpoint_schema_sha256`: `63c73293084fc3a30f77da375e694f443e972d049ec667d9d20e09b849920888`.

**Important:** Cryptographic digest equality proves artifact-byte custody against the declared manifest, not human truth, rights, provenance authenticity, semantic model quality or permission for future real training.

## Sixteen-control Part B acceptance matrix on exact B v2

| Control | Verdict and bounded evidence |
|---|---|
| A01 byte/special noncollision | **PASS_C_SCOPED** source and QA |
| A02 chat template/role/EOT/EOS | **PASS_C_SCOPED** independent manual role wire |
| A03 role provenance/mask bit flip | **PASS_C_SCOPED** all-bit negative tests; declared roles not externally authenticated |
| A04 +1 target alignment | **PASS_C_SCOPED** x/y known-answer comparison |
| A05 stop supervision | **PASS_C_SCOPED** assistant EOT/final EOS supervised, **user EOT not supervised** |
| A06 ignore_index=-100, prompt-target CE zero | **PASS_C_SCOPED** no direct prompt label CE; contextual gradients allowed |
| A07 actual B loss path | **PASS_C_SCOPED** P02 logits + `cross_entropy_valid` independent CE oracle; no default unmasked loss |
| A08 padding and no packing | **PASS_C_SCOPED** right pad, one dialogue/row for physical bundle |
| A09 causal attention | **PASS_C_SCOPED** bounded CPU P02 future isolation |
| A10 finite forward/backward | **PASS_C_SCOPED** bounded CPU, prompt contextual derivative positive, optimizer steps 0 |
| A11 context limit | **PASS_PACK_SCOPED** emitted real model-bound rows length32, max_len33; generic B standalone oracle supports max257 and **must not** be called directly with >33 for P02 |
| A12 checkpoint/version lock | **PASS_C_SCOPED** metadata-only, old/new mismatches fail closed; historical weights not loaded |
| A13 byte provenance/role literals | **PASS_C_SCOPED** strict UTF8/NUL/Unicode; roles are declared, not authenticated corpus provenance |
| A14 seven real SHA/alias/tamper | **PASS_C_SCOPED** 7/7 physical GitHub SHA plus C independent mutation tests |
| A15 exact B/C import interface | **PASS_C_SCOPED** C Part A routed by B; C own independent test imports B implementation and exact C oracle on review branch |
| A16 native / final adjudication | **HOLD_DISTINCT_REVIEWER** — C cross-track CI is not the third-party reviewer and PM has not accepted BC-5 |

**C contract verdict:** `C_CONTRACT_COMPATIBILITY_PASS_SCOPED` on exact B code HEAD `724f62a0...` and byte-identical evidence continuation `888acd45...`; not a blanket endorsement of future B changes or a PM-level `BC_INTERFACE_PASS_ENGINEERING_SCOPED`.

## Residual risks (scoped, not retrospective v1 blockers)

1. B's generic `serialize/build` permits max_len up to 257 to exercise C's reference; real P02 model context is 32. Current `write_bundle` and `synthetic_cpu_probe_v2` strictly use max_len33. Future trainer API should enforce this bound explicitly; no permission to run real SFT.
2. B `verify_bundle` currently rejects symlinks on seven artifact paths/root but does **not explicitly reject a symlink at `manifest.json`**. Distinct reviewer should assess this within the current single QA packet; a trusted repository/CI fixed path is lower risk than arbitrary external input.
3. GitHub Actions author and C review environments are GitHub-hosted Python3.12, **not the owner's native Windows Job Object resource-cap test**. B-M3 prior PM PASS scoped, V3 immutable HOLD and reviewer `HOLD_PEAK_ACCOUNTING` dissent must all remain in lineage as separate facts; **BC-5 is HOLD**.

**No edit by C** to PR #34/#36 branches, `main`, `lineage.md`; no SFT science, GPU, real data/checkpoints, historical TEST, optimizer, merge or owner GO.

**Bước thực hiện tiếp theo — duy nhất:** `TTM_PM_BC_F01_F04_WIRE_SCHEMA_HASH_BRIDGE_INTEGRATED_AMENDMENT_AND_DISTINCT_QA_SINGLE_GATE` — distinct reviewer rechecks exact B code + source pins + seven actual artifacts and resource predicate, then PM issues a single engineering `PASS/HOLD` adjudication without micro-permits or V3 rerun.
