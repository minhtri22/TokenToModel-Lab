# TTM T2 — CPU Synthetic GGUF Implementation / Integrated QA Receipt (2026-11-08)

**PR:** #12 (DRAFT). **Base** `main@1a9d8cba56564d6d36257fe95c34f2fd52c4f48a`.  
**Source P02 Git blob:** `9762343e06cf800b50574c2871ae1ed58537fb18`.  
**Pinned target:** `ggml-org/llama.cpp@372dc5ca157276beb6c67b2e92477e8d662e964a`.  
**Output:** T2 implementation bundle `TTM_SMALL4M_T2_GGUF_CPU_QA_V1_20261108.zip` (not yet committed to GitHub). ZIP SHA-256 `F63123689CCD3D25A02A288CFC82D887615ECBBAC98424895CC9B7D0BF912D00`.

## Execution scope

Executed locally in ephemeral container CPU with `torch 2.10.0+cpu` and Python 3.13, against an **exact byte-for-byte Git blob** of repository P02 (`sha1('blob <size>\\0'+source)` = `9762343e...`). This is an isolated source mirror for reproducible QA, *not* an edit to GitHub/local Windows. No TinyStories data, training, Colab, GPU, source publication, or scientific TEST.

Bundle contains `t2_gguf_cpu.py`, `t2_llama_parity.py`, native `llama_logits_probe.cpp`, `CMakeLists.txt`, `test_t2_gguf_cpu.py`, a PowerShell 5.1 Windows runner, and `T2_QA_REPORT_20261108.json`. PowerShell 5.1 runner is **not yet dynamically parsed/tested on user's Windows**.

## Measured QA

| Check | Verified result |
|---|---|
| Model config | vocab 2048, context 256, layers 4, heads 4, n_embd 256 |
| Unique parameters | **3,749,376**, tied output-head |
| GGUF tensor mapping | **52/52** tensor names, shapes and types parsed on readback |
| GGUF F32 | **PASS** structural/weight readback; size **15,051,712 bytes**, max error **0.0** |
| GGUF F16 | **PASS** structural/weight readback; size **7,552,960 bytes**, max error **3.0517578125e-5** |
| F32 SHA-256 | `b1b22687b60c65da2d585da5f8b553398cb537b3caa3f465532edd0092102bd8` |
| F16 SHA-256 | `a2b90ec458b592ce38bae4588a8db60660ab92add08491f80662d5d0a7d937cd` |
| Synthetic BPE structural contract | 256 byte IDs + EOS=256 + 1791 deterministic synthetic pair merges |
| CPU pytest | **9/9 PASS** (including overwrite, header corruption, truncation, source tamper negatives) |
| Actual pinned llama.cpp binary load | **NOT EXECUTED**: binary not installed in isolated CPU runtime |
| PyTorch ↔ llama.cpp logits CPU parity | **NOT EXECUTED** |
| llama.cpp tokenizer vs TTM surrogate BPE | **NOT EXECUTED** |
| Full T2 integrated verdict | **HOLD_LLAMA_CPU_BACKEND_AND_TOKENIZER** |

**Important mapping finding:** TTM `nn.Linear` tensors are already `[out,in]` in PyTorch; direct row-major GGUF tensor payload is correct. The upstream HF GPT-2 converter transposes because HF `Conv1D` stores `[in,out]`; applying that transpose to TTM tensors a second time would be a defect. Converter/backend existence and self-readback **do not prove** backend logits parity.

**Tokenizer risk:** Surrogate BPE is *whole-string byte-level* while GPT-2 tokenization applies a pretokenization regex. Text with whitespace/newlines or Unicode must be compared using actual `llama_tokenize`; mismatch is a real T2 failure requiring a compatible adapter/tokenizer strategy, not a reason to silently change model or science criteria.

## Full test prescribed on Windows CPU (not yet executed)

- Verify same pinned repo/source; run `-Mode Preview`, then `-Mode Execute` from the ZIP; optional `-AcquirePinnedLlamaCpp` only for **llama.cpp source**, not TinyStories. Existing source can be supplied via `-LlamaSource`.
- Native C++ probe at pinned upstream has full 2,048-d logits, explicit token-ID inputs and 9 tokenizer fixture inputs. CPU F32 max absolute logit error must be `<=1e-3`, F16 `<=2e-2`, all eight numerical fixtures and nine tokenization fixtures; top-1 must match. Failures must stay FAIL, not marked PASS.
- Save console and final SHA/QA artifact. Review isolated code with exact SHA before integrating with PR #12. Do **not** launch long Colab training when backend/tokenizer parity is unproven.

## Governance

`TTM_T2_STRUCTURAL=PASS` · `T2_WEIGHT_READBACK=PASS` · `T2_PYTHON_9_OF_9=PASS` · `T2_LLAMA_CPP_CPU=NOT_EXECUTED` · `T2_FULL=HOLD` · `SCIENCE_LOCK=HOLD` · `COLAB_T4_GPU=NOT_USED`. No `lineage.md` mutation. This receipt records technical QA only, **not a scientific PASS**.

**Bước thực hiện tiếp theo:** Run the exact pinned CPU backend/tokenizer/logits QA from the reviewed bundle on Windows; after its receipt, either admit T1/T3 or classify T2 mismatch and repair only the adapter. Do not rerun science.
