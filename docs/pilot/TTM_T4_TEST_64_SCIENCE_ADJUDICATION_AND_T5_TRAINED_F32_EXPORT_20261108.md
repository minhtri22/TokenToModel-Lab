# TTM-Small4M — T4 sealed 64-story TEST and trained T5 F32 GGUF adjudication (2026-11-08)

**Scientific TEST verdict: PASS_TEST_HOLDOUT_DESCRIPTIVE_SCOPED (original one-shot report / provenance verified).** **T5 conversion verdict: PASS_F32_TENSOR_AND_BPE_PRODUCER_READBACK.** No model retraining, no re-evaluation of TEST, no data/model selection, no GGUF backend execution.

## Frozen science provenance

- Prior H1 preregistered **on VAL only**, independently reproduced: model NLL 3.522338851682218, TRAIN-only Add-alpha=0.1 bigram NLL 3.9972314169551506, 11.880537% relative improvement, 95% bootstrap per story [0.4581867476104475,0.49406158185105853]; recorded as L0011.
- Final step1024 checkpoint SHA256 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`, exact existing P02 model, TEST never used to choose this checkpoint.
- T1 original split manifest SHA256 `9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9`; 64 frozen TEST story identities from `splits.TEST`; T1 TRAIN BPE manifest SHA256 `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`; pinned original valid source SHA256 `94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4`.
- TEST RunID `ttm_t4_test_64_step1024_one_shot_20261108_v1`. User Windows execution `T4_TEST_ONE_SHOT=COMPLETED_UNADJUDICATED` following `PASS_READONLY_64_SEALED`. Read-only remote workspace independently confirms `CLAIM.json` preceding the one-shot result and only these two files in output directory. Both are archived in `evidence/pilot/t4-science/` as original Windows-CRLF bytes with Git readback PASS.
- TEST producer report original SHA256 **`7df02a53cb84d3026f3b259154e0c4f3dcc5fa27e16170e740fd570df059a50d`**. Independent byte-format reconstruction from the remote-read JSON and Python's Windows text-mode CRLF writing rules reproduces this SHA256 exactly, **without reading TEST data or rerunning evaluation**. Git blob `0b24ea7be55a305196962f75e65bdfd87ebf4898`.
- No raw stories, tokenized TEST windows, original checkpoint, or trained GGUF committed into public GitHub.

## 64 TEST story result — one-shot held-out descriptive

| TEST statistic (64 stories, 76 windows, 14,669 next-token targets) | Value |
|---|---:|
| Trained model mean NLL | **3.483591073340649** |
| Frozen TRAIN-only bigram Add-0.1 mean NLL | **3.97360374531842** |
| Unigram TEST mean NLL | 5.990914186352912 |
| Absolute bigram-model advantage | **0.4900126719777709** |
| Relative NLL improvement | **12.331694436%** |
| Story bootstrap 1,000 resamples seed20261109, 95% absolute advantage CI | **[0.45801078384645544, 0.5216391152410562]** |
| Applying unchanged VAL threshold (5% improvement & lower CI >0) | **BOTH_MET_DESCRIPTIVE** |

The independent review cross-checked the arithmetic of `(bigram-model)/bigram`, original checkpoint/split/BPE IDs, completeness (64 stories and 14,669 labels), and the one-shot source procedure `score_test` (TRAIN-only bigram; once-per-story tokenization; bootstrap over TEST stories). **This is not an independent per-token recomputation of TEST NLL**: the one-shot TEST remains consumed and the original report is the only scientific measurement of TEST.

**Reporting-label caveat:** The original TEST result intentionally reuses the frozen generic evaluator schema `ttm.t4.h1.val.storybootstrap.v1`, names numeric fields `primary_*_val_nll` and retains the evaluator's stale phrase `VALIDATION-only... TEST sealed`. These are inherited schema/wording labels, **not** evidence that VAL rather than TEST was evaluated: outer receipt explicitly records `eval_set=SEALED_TEST_64`, `test_stories=64`, `test_windows=76`, `test_tokens_saved=false`. Do not modify the original artifact or rerun TEST to repair labels. Formal interpretation remains descriptive held-out corroboration, not a second primary H1 prereg.

## T5 F32 trained GGUF

- Separate user Windows `-Mode T5Preview=PASS`, `-Mode T5Export=PASS_EXACT_PYTORCH_GGUF_READBACK`; no TEST access; output `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t5_trained_f32_v1\TTM-Small4M-T4-step1024-F32.gguf`.
- Report `evidence/pilot/t5-trained/T5_TRAINED_GGUF_F32_EXPORT_READBACK.json`, original-CRLF archive Git blob `486c9743f023763c3217f3a971fb86502466c288`. Original reported GGUF SHA256 `5bdc904e6c51af04a4223219f36e6bc2e687f60fd6e17dc24508f3eb7489e4e5`, **15,061,376 bytes**.
- Exporter loaded the exact trained checkpoint and original TRAIN-fitted tokenizer: **52/52 F32 tensors exact PyTorch readback**, 2,048 real tokens, 1,791 real merges. These are exporter self-QA plus independent inspection of the receipt, **not a separate byte readback of the GGUF via remote**.
- **`T5_TRAINED_LLAMA_CPP_PARITY=NOT_EXECUTED`**; **`T5_OLLAMA_RUNTIME=NOT_EXECUTED`**. Prior T2 parity used untrained weights, so cannot establish T5 runtime parity. Ollama may reject this custom GPT-2 GGUF; record backend BLOCKED if it does.

## Follow-on action (technical, not a repeat of TEST)

Use existing pinned T2 llama.cpp root `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\llama.cpp` and existing compiled probe `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t2\build\Release\ttm_t2_probe.exe`; DLL directory is `...\build\bin\Release`. Run **only trained GGUF** 8 full-logit/9 tokenization fixtures with `T5LlamaParity` from frozen handoff; no TEST dataset, model training, or GGUF reexport. Preserve PASS/FAIL report. If llama.cpp passes, then assess Ollama import and inference (separate binary compatibility outcome).

## Governance

T4 scientific training/VAL H1 remains PASS L0011; this TEST descriptive one-shot warrants one **append-only L0012** lineage entry, with the above limitation and no inference of human-perceived story quality. Archive the exact implementation ZIP SHA256 `889f660138e013cceb70a5b88016f2dec850976cb028b36ee180908036dab369` (new source bundle itself not yet committed as executable source under PR #12; frozen source and producer script have been reviewed in conversation). PR remains draft; main unchanged.

**Next:** `TTM_T5_TRAINED_F32_LLAMA_CPP_PARITY_AND_OLLAMA_RUNTIME_QA`. Do not rerun TEST or TRAIN.
