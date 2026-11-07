# TTM P07 — G0 capability preflight and G1 paged-attention kernel contract (v1)

Date: 2026-11-07. Classification: **DESIGN_AND_CONTRACT_LOCK_ONLY**. No GPU kernel implementation/dispatch, installation, driver change, P08, real-corpus access, or Git main update.

## Frozen ancestors and exact scope

| Item | Pin |
|---|---|
| Repository | `https://github.com/minhtri22/TokenToModel-Lab.git` |
| Main/P06 merge commit | `4731f75cda6aa86b1dd2929b3f10d11fbbed0812` |
| P07 design branch prior to this lock | `feature/p07-paged-attention-kernel-design-20261107` at `a1a5fde085bacce834656c0d5140e1cb5b433b51` |
| P06 Paged KV CPU oracle | `src/p06/paged_kv_manager.py`, Git blob `4d52188adaf55674b6965513ea1beb38ec9a8e9b` |
| P05 Dense KV CPU oracle | `src/p05/dense_kv_cache.py`, Git blob `d835e5d7bb07fea447c5a869b13c70327ab05a53` |
| P02 Transformer reference | `src/p02/transformer_core.py`, Git blob `9762343e06cf800b50574c2871ae1ed58537fb18` |
| P00 Paged KV reference | `reference/phase0/paged_kv.py`, Git blob `ead322ff7559686cd8989264506cee6dd54c7441` |

`lineage.md` is not modified here. P01–P06 are frozen. P07 `DESIGN_ONLY`; P08 not opened. Scope is **synthetic token IDs 0–2047** and reference decoder inference, never F1 WP30/TEST or P03/P04 scientific training/evaluation.

## G0 — read-only Windows observation contract

The approved **downloadable, local-only** probe is `TTM_P07_WINDOWS_GPU_READONLY_PREFLIGHT_PS51_V1_20261107.ps1`, SHA-256 `31d3196398950fe25671eeb7cf3d72d8dd83043ce2def51c93cb53a8f143600e`. It is provided in the bundled ZIP, **not committed to the GitHub branch in this step**. The ZIP also contains its SHA-256 manifest. It:

1. Uses read-only Git commands (`git -C <TTM> remote get-url origin`, `rev-parse`, `status` with optional locking disabled). It **does not fetch, checkout, merge, pull, prune, modify worktree, or synchronize local main**, even if local HEAD remains stale at `92facee...`.
2. Reads Windows OS/CPU/free RAM and D: free space, `Win32_VideoController`, display-class `Win32_PnPSignedDriver` (no full PnP serials), installed command paths (`icx`, `icpx`, `dpcpp`, `sycl-ls`, MSVC, CMake) and well-known oneAPI directories.
3. Probes only **already existing** Python interpreters via `python -B -I -c`; reads PyTorch version/installed-package metadata, `torch.xpu.is_available()`, `device_count()` and GPU device name if available. Queries may initialize an XPU runtime, but **do not allocate GPU tensors or dispatch kernels**. Some third-party imports may have side effects outside this script's direct control; this probe imports only `torch` and Python standard library.
4. Prints one JSON record between `TTM_P07_GPU_PREFLIGHT_JSON_BEGIN` and `_END` and a short verdict. Script itself writes no receipt file; original console output is the evidence to submit for independent review. No credentials/username/full PnP path need be committed to GitHub.

This record cannot itself **prove** a custom GPU kernel works: G0 reports device, driver and compiler visibility only. A missing compiler on `PATH` does not prove it is uninstalled. A CPU PyTorch wheel (`+cpu`) does not prove the Intel GPU is unsupported.

## Backend decision matrix (sources reviewed 2026-11-07)

| Candidate | External support | P07 disposition until machine evidence |
|---|---|---|
| Intel oneAPI DPC++/SYCL + Level Zero, Windows | Intel lists Windows and Intel Arc; current release notes include Lunar Lake/Xe2 | **Preferred conditional candidate** for a native direct-paged-KV kernel, not yet selected/validated |
| PyTorch XPU native, Windows | PyTorch documents Intel Core Ultra Series 2 Lunar Lake on Windows 11 | **Integration/oracle layer candidate**, not itself proof of direct physical-block reads in a custom P07 kernel |
| Intel XPU Triton Windows | Upstream Windows path is experimental, source build required; published validated hardware list excludes Arc 140V | **Not selected** without a separate compatibility demonstration; no package installation in G0 |
| CUDA | NVIDIA-specific | Out of scope for Intel Arc hardware |

Sources: PyTorch Intel GPU getting-started (`https://docs.pytorch.org/docs/main/notes/get_start_xpu.html`); Intel oneAPI compiler (`https://www.intel.com/content/www/us/en/developer/tools/oneapi/dpc-compiler.html`); Intel oneAPI 2026 release notes (`https://www.intel.com/content/www/us/en/developer/articles/release-notes/oneapi-dpcpp/2026.html`); Intel XPU Triton Windows (`https://github.com/intel/intel-xpu-backend-for-triton/blob/main/.github/WINDOWS.md`). The docs support *possibility*, not installed capability.

**G0 decision rule:** `G0_BACKEND_RUNTIME_CONFIRMED` only after a real Windows receipt shows Intel GPU identity, driver and a compatible XPU runtime or native compiler installed. **No custom kernel viability claim** until G1 execution. If missing, remain `G0_CAPABILITY_GAP`; do not silently install/update or switch to an NVIDIA backend. Selection of compiler/linking or backend still requires additional build/runtime evidence; this lock is the *interface and QA method*, not a false runtime permit.

## G1 — numerical GPU kernel interface frozen before execution

At first implementation, one direct-read GPU paged-attention decode step shall consume:

- `pool[L, 2, Nblocks, B, H, D]`, initially `float32`, based on P06 physical storage; K/V axis `0/1`.
- Per-request `page_table[R, ceil(Tmax/B)]` with integer physical block IDs; invalid/padding slots are `-1`. `lengths[R]` and `request_row` map to the corresponding request ID; physical page ownership is validated outside the kernel and enforced by negative QA.
- Query tensor for a *single decode position* `q[H,D]` and layer `ell` (`0 <= ell < L`), token position `t`, block size `B`, head count `H`, head dim `D`.
- For any preceding position `j` in `[0,t]`, **direct index** `p = page_table[request_row, j // B]`, `offset = j % B`; read `k_j=pool[ell,0,p,offset,:,:]` and `v_j=pool[ell,1,p,offset,:,:]` *without gathering all pages into contiguous dense KV first*.
- Compute attention per head `softmax_j(q_h · k_{j,h}/sqrt(D))` and `y_h = sum_j(attn_j * v_{j,h})`. No future tokens, no cross-request pages, no shared-prefix/COW/batching scheduler.
- `y[H,D]` is passed through P02 projection/residual/MLP at identical model weights to produce per-step `logits[2048]` for comparison with P06, P05 and no-cache P02. Define GPU tensor layouts and any host/GPU transfer boundary in the future implementation record before running.

**Negative conditions:** malformed/unallocated/duplicate-offending page mappings, missing or released request, zero/overlong context, OOM, wrong layer, shape/dtype mismatch, interleaved isolation and released page zeroing must fail without cross-request data leak or state mutation. Allocation/release authority remains outside kernel; P06 page-table rules are oracle.

**Locked initial float32 parity criterion:** each step's logits vs P06/P05/P02: `torch.testing.assert_close(atol=2e-4, rtol=2e-4)` with finite outputs; additionally compare attention output `y[H,D]` against independent PyTorch scaled-dot-product reference. Any proposal to change tolerance or dtype must be registered **before** viewing the confirmatory numerical result. FP16/BF16 are separate successor gates, not implicitly covered by fp32 PASS.

## G2 — equivalent workload/performance gate (not executed in G0)

Compare P07 to a compatible **same GPU/dtype** baseline at matched `(batch, seq_len, block_size, H, D)`, controlled warmup and device synchronization, multiple repeats, latency distributions and peak allocated memory. Include at least `seq_len` crossing block boundaries and interleaved request workloads; record fragmentation. CPU P05/P06 remain numerical references, not GPU performance baselines. **Do not claim speedup** from unsynchronized or 2-repeat timing data.

No implementation, GPU kernel execution, model training, driver update, package install, or P08 step is authorized by this document. A future independent QA/merge decision must preserve every PASS and FAIL and maintain `lineage.md` as scientific-only append-only history.

**Next step:** `TTM_P07_G0_WINDOWS_READONLY_RECEIPT_REVIEW_AND_BACKEND_DISPOSITION` — collect the read-only console JSON on target Windows, independently inspect it, decide whether the SYCL/Level Zero candidate is viable or blocked. Keep P07 `DESIGN_ONLY` until that decision.
