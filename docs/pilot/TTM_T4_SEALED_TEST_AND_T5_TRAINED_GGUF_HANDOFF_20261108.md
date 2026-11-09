# TTM Small4M — T4 TEST one shot and T5 trained F32 GGUF handoff (2026-11-08)

**Status:** H1 VAL PASS independently; 64 sealed TEST stories NOT ACCESSED in this turn; trained T5 GGUF on Windows NOT EXECUTED; llama.cpp/Ollama trained backend NOT EXECUTED. Main, P00–P12 and previous lineage unchanged.

## Frozen inputs

- Trained final checkpoint step1024: SHA256 cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b, 45,074,891 bytes, private Drive https://drive.google.com/file/d/1F4kaaaC7w3MVPyPFoFa4BpGyWu0LLLme/view
- 64 selected TEST story SHA IDs from original immutable T1 split manifest SHA256 9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9 on local Windows; no new split or model selection.
- Raw TinyStories-valid.txt SHA256 94e431816c4cce81ff71e4408ff8d3bda9a42e8d2663986697c3954288cb38b4; TRAIN-only BPE manifest SHA256 cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc; TRAIN/VAL private NPZ SHA256 184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913.
- P02 exact Git blob 9762343e06cf800b50574c2871ae1ed58537fb18; science lock SHA256 fd183ade2a696d40313aae19b63429d4ef3edd8abf25c899c8cc496836d36817.

## Executable artifacts prepared (NOT science evidence)

- Frozen ZIP **TTM_T4_SEALED_TEST_AND_T5_TRAINED_GGUF_HANDOFF_20261108.zip** SHA256 **889f660138e013cceb70a5b88016f2dec850976cb028b36ee180908036dab369**, size **35,103 bytes**, 12 members, 11-member SHA/CRC readback exact. ZIP exists as a conversation artifact, not as separately committed source files in this PR.
- One-shot Windows Python TEST evaluator: preflight validates original hashes without scoring TEST, TestOnce creates exclusive CLAIM.json before any TEST story decoding, produces only aggregate metrics (NLL/CI/64-story counts), never raw TEST/token files; refuses reruns with same RunID even on failure. Output private scoped local _tmp/ttm_t4_test_64_step1024_one_shot_20261108_v1.
- Separate T5 F32 converter loads **trained** 1024 checkpoint and **real TRAIN-only BPE2048**, reuses pinned T2 GGUF tensor mapping, checks all 52 F32 weights byte-equivalent and metadata 2048 tokens/1791 merges, writes project-local _tmp/ttm_t5_trained_f32_v1/TTM-Small4M-T4-step1024-F32.gguf; no TEST access or overwrite.
- Separate trained llama.cpp F32 parity checker: pinned llama.cpp SHA 372dc5ca157276beb6c67b2e92477e8d662e964a; 8 complete 2048-logit probes, <=0.001 worst absolute error, top1 zero errors; 9 tokenizer GPT2-BPE strings 100% match; no claim until actual Windows execution.
- Ollama model-from-GGUF import remains a **runtime-dependent test**, not guaranteed by the GGUF export or the model's VAL NLL. Log unsupported architecture as BLOCKED and do not edit trained weights to conceal it.

## Technical QA already executed without TEST

- Independent package Python AST and source member SHA PASS; synthetic 64-story token-window/evaluator smoke PASS.
- The **actual frozen step1024 trained checkpoint** was converted in a temporary directory to F32 GGUF with synthetic QA tokenizer only: 52/52 trained weight tensors exact readback PASS, 15 MB. Temporary synthetic-tokenizer GGUF discarded. **This is NOT a final trained model with its actual TinyStories tokenizer.**

## Next exact Windows action

1. Download the pinned 45MB checkpoint from the private Drive into Downloads/checkpoint.pt and SHA-verify. Extract the ZIP into Downloads/TTM_T4_TEST_T5_HANDOFF_20261108; use the project's existing CPU Python with torch/numpy/regex.
2. Run PowerShell 5.1 launcher Invoke-TTM-T4-TEST-T5-PS51.ps1 with -Mode TestPreview (only source SHA/read-only); on PASS, run -Mode TestOnce exactly once. No auto-rerun even if the attempt fails. Do not disclose raw TEST content.
3. Run -Mode T5Preview then -Mode T5Export separately, independent of the TEST result. Read output GGUF SHA and report, test trained llama.cpp native probe after the file exists.
4. Independently read back each sanitized receipt and append a scientific TEST PASS/FAIL/INCONCLUSIVE entry to lineage.md without rewriting prior L0011; T5 technical output belongs in evidence/docs, not scientific lineage.

**Next:** TTM_T4_TEST_64_SINGLE_CLAIM_AND_T5_TRAINED_F32_WINDOWS_READBACK. T4 TRAIN is closed; no reruns, no new TEST content in GitHub.
