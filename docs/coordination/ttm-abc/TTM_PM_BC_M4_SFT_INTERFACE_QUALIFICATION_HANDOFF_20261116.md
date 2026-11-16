# PM HANDOFF — Track C M4 PASS_DESIGN → Track B/C SFT Interface Qualification

**Operation:** `TTM_PM_BC_SYNTHETIC_SFT_INTERFACE_QUALIFICATION_SINGLE_GATE`  
**Date:** 2026-11-16 · **Authority:** owner accepted three-track PM program; this is engineering-only QA design, **not** new science/SFT training authorization.  
**PM issue:** [#32](https://github.com/minhtri22/TokenToModel-Lab/issues/32)  
**Track B source:** [Draft PR #34](https://github.com/minhtri22/TokenToModel-Lab/pull/34) exact HEAD `43896bcd034c82e8433bc6a2b53eefbd936616fb` (B0/B1 author CI on `ff2dc7c59258079a5f3fc5f1bcf4e60c3cfc279e`).  
**Track C source:** [Draft PR #35](https://github.com/minhtri22/TokenToModel-Lab/pull/35) exact HEAD `185d465c31f5f4bef6220be95e39dac1ae81c5b8`.  
**C independent re-review:** [review](https://github.com/minhtri22/TokenToModel-Lab/blob/9fac5a675955d8b91d6855d27907f239cbfb745f/docs/research/ttm-abc/track-c/independent_review/C_M4_EXACT_AMENDMENT_DISTINCT_REREVIEW_20261116.md); [QA receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/9fac5a675955d8b91d6855d27907f239cbfb745f/artifacts/ttm-abc/track-c/TTM_TRACK_C_M4_EXACT_AMENDMENT_DISTINCT_REREVIEW_RECEIPT_20261116.json). Author 24 tests + distinct reviewer 9 + historic red 2 = 35/35; Python3.13.5/Linux stdlib only.  
**Verdict:** `C-G5=PASS_DESIGN_SCOPED_B_INTEGRATION_NOT_EXECUTED`; `C-G1=HOLD`, `C-G2=DESIGN_VALIDITY_UNPROVEN`, `C-G8=NOT_EXECUTED`. PR remains draft. Prior HOLD is preserved as historical finding.

## 1. Program dependency status

- Track B B0/B1 GitHub Actions independently read back: 21/21 author tests on Windows Python3.12/PowerShell5.1 and Linux Python3.12; 3+5 synthetic resume E2E. **B-G5=HOLD_OWNER_NATIVE_HARD_RESOURCE** and **B-G6=HOLD_DISTINCT_NATIVE_QA**; no model-quality inference. Owner's V1 Windows OnePack at exact B SHA produced `PHASES_RUN=0`, `HOLD_NATIVE_QA` due to missing local Git commit and PowerShell 5.1 expected-native-stderr behavior. Receipt SHA256 `de889cabc5c7ac7057da9d1a4485c0f83077163f14beddf2a4153ef171f427d8` is preserved. V2 wrapper repairs only fetch/probe behavior; it has **not yet passed** the owner workstation.
- C-F01 is closed **for design**: zero direct CE loss on prompt targets is required; nonzero gradient via prompt context **must not** be forbidden.
- C-F02 is closed **for toy role/mask structure**: `build_sft_targets` derives flags from conversation, `shifted_padded_targets` validates flags against reparsed roles; caller-provided role identities/source authenticity, real-tokenizer IDs and dataset rights remain separate.
- C-F03 NFC/casefold duplicate collision test is scoped toy PASS, not corpus near-duplicate science.
- **Do not claim compatibility just because vocab=2048 in both tracks.** B synthetic tokenizer uses literal byte IDs 0..255 and EOS 256; C toy has PAD/BOS/SYS/USER/ASSIST/EOT/EOS = 0..6 with arbitrary content IDs >=7. Direct concatenation/copying causes **special-token collisions**. B's existing synthetic pack validator accepts only <=256 and cannot be reused unchanged for a new SFT chat pack.
- B's P02.forward default unmasked CE is not an SFT loss implementation; use B's explicit masked `cross_entropy_valid(...,ignore_index=-100)` or equivalent tested adapter. No historical T4 checkpoint loads, source tokenizer swaps or checkpoint reinterpretation.

## 2. One integrated prospective **synthetic CPU** interface qualification

**Task owner:** B authors the integration adapter, C supplies the reviewed role/mask oracle; an independent reviewer adjudicates exact source HEAD. Neither agent may edit the other agent's historical source branch directly; submit a separate scoped draft integration PR or B-scoped candidate with explicit C blob pin and PM acceptance. No micro-permits or GPU.

Required contracts and explicit synthetic-only tests:

1. **Tokenizer and role-ID wire:** Version an actual B-facing synthetic chat codec, with noncolliding and distinct bytes/special IDs; one *candidate* allocation (not automatic acceptance) using vocab=2048: byte content 0..255; EOS=256; PAD=257, BOS=258, SYS=259, USER=260, ASSIST=261, EOT=262. Keep tokenizer config/ID map + vocabulary and chat template SHA256; assert no role delimiter leaks inside content, byte roundtrip, EOS/turn stop, no double EOS. Introduce a NEW SFT pack schema, not `ttm.track_b.synthetic.byte_windows.v1`.
2. **Shift/alignment:** `input_ids[:-1]` versus `input_ids[1:]` with target labels `IGNORE=-100` for SYS, USER, headers, PAD, and BOS. Supervise assistant answer bytes and assistant EOT/EOS only. Assert each supervised target belongs to a trusted role span under the chosen template. No all-ignore. No silent truncation or invalid role sequence.
3. **Masked CE + context gradients:** Compare B masked CE to an independent oracle as SUM(valid-target CE)/count. Negative tests: flip each flag, inject reserved role tokens, wrong target shift, leaking user target, mismatched EOS, wrong tokenizer/codec SHA. Explicitly permit prompt-context/embedding gradient while ensuring the direct CE term for prompt target positions is absent. A single bounded synthetic CPU forward/backward verifies that model gradients remain finite, assistant labels are counted and masked positions do not produce direct loss; it is **not new SFT training/science**.
4. **Padding/attention:** On P02 causal attention, verify no future leakage and padding positions excluded from loss; if positions are padded on the left or packed across conversations, test attention isolation or **do not enable those modes**. First implementation may restrict to right padding, one conversation per row with no packing.
5. **Checkpoints and reproducibility:** Do not load historical T4/P04 weights. Freeze synthetic fixture, exact B/C source/blob SHA, code config, ChatTemplate, model config, outputs, Python/torch and predeclared resource caps. Negative tests must reject old B byte-pack schema applied to new special IDs and disallow resume across changed token mapping without a new checkpoint schema. Run Windows Python3.12 synthetic-only QA after B's native resource gate, or mark that lane `NOT_EXECUTED`.
6. **Independent adjudication:** one review covering (a) exact SHA and source import boundary, (b) masked CE and +1 shift, (c) tokenizer noncollision, (d) role/mask negative controls, (e) finite gradient/causal padding, (f) resource guard and no new science. Record `BC-SFT-INTERFACE_PASS_ENGINEERING_SCOPED` or `HOLD_INTERFACE` with a single defect; this is separate from C-G1/C-G2/C-G8 and B-G5/G6.

### Gate acceptance

| Gate | Required evidence | Initial state |
|---|---|---|
| BC-0 | Exact B/C SHA, interface specification, independent source check | NOT_EXECUTED |
| BC-1 | Noncolliding codec special map + byte/role roundtrip + negative ID collisions | NOT_EXECUTED |
| BC-2 | Trusted role provenance, +1 shifted labels and ignore_index masked CE oracle | NOT_EXECUTED |
| BC-3 | Finite CPU synthetic backward, causal/padding isolation, no leakage | NOT_EXECUTED |
| BC-4 | Schema/hash/resume mismatches reject safely, no old T4/P04 loading | NOT_EXECUTED |
| BC-5 | Scoped native resource + independent exact-HEAD QA, GitHub receipts | WAIT_B_G5_G6 |

**Output:** `docs/research/ttm-abc/bc-sft/BC_SFT_INTERFACE_CONTRACT.md`, synthetic test scripts/config, independent QA receipt, exact source SHA list and **one** gate decision. Keep main, PR34/35 and lineage unchanged; this PM handoff is a separate coordination branch. No model training on real data, no GPU, no hidden TEST.

**Next single program operation:** `TTM_PM_BC_SYNTHETIC_SFT_INTERFACE_QUALIFICATION_SINGLE_GATE`; for Track B owner-host native QA the narrower prerequisite is `B_B0_B1_OWNER_WINDOWS_PY312_HARD_RESOURCE_QA_AND_FINAL_PM_ADJUDICATION`. C is free to proceed with independent design work while BC interface remains pending.
