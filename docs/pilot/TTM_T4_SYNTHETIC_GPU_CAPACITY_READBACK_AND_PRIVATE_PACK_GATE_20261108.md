# TTM T4 — Colab Tesla T4 synthetic capacity independent readback (2026-11-08)

**Scope:** capacity measurement only, **not** TinyStories training. PR #12 remains DRAFT; science lock HOLD. P00–P12 / P07 / append-only `lineage.md` unchanged.

## Provenance

- Colab runtime: **Tesla T4**, **PyTorch 2.14.1+cu130**, CUDA 13.0, frozen P02 Git blob `9762343e06cf800b50574c2871ae1ed58537fb18` and 3,749,376 unique parameters.
- One-shot run `t4_capacity_synthetic_20261108_v1`, user independently executed notebook code cells and `drive.flush_and_unmount()` completed.
- Raw Drive folder: https://drive.google.com/drive/folders/1YrmbEV-0CW_ijxl7jvAho6N2dMy4Mmtk
- Independently downloaded all **four entire files** via Google Drive connector, recomputed their byte SHA256, verified `READY.json` report/env/pip fields against the actual bytes, and uploaded the **exact bytes** to `evidence/pilot/t4-capacity/` on PR #12; every Git blob readback matched independently computed blob SHA1.

| File | SHA256 actual Drive bytes | Git blob SHA1 |
|---|---|---|
| `T4_CAPACITY_REPORT.json` | `c55a568496a888bc3abc95c0231a5ed17d3a6f366361571b6f89a4457d09f1ee` | `43f59354bfc3bd6304b0c8174e56ef55af597f55` |
| `READY.json` | `00f776e27b462a9b12112e91df27aa4a90f9157ab050a07f103292ecbf5f44b3` | `3e0d45c47b4a5caf44de9b8f733e83b4ac3f0138` |
| `COLAB_ENVIRONMENT.json` | `9784f2c48e91f053ceb423f8dd77bd2af1c8f202c1d733bc4bf4dfb589a18802` | `162722550c33530da1a8d0aa1b31c7a4c3b47d33` |
| `COLAB_PIP_FREEZE.txt` | `a6eebfff272109bc4732b72d4bb1a0892d73e3db37c8f35d3afd7f32dcff0b80` | `056c738d87865d6632e80c03262b28fc1e5b8456` |

## Results (synthetic full-length 256-token windows, 4,096 scored targets per optimizer step)

| Mode | Microbatch windows | Gradient accumulation | Worst step (seconds) | CUDA memory reserved GiB | 1,024-step extrapolation with 25% reserve (seconds) |
|---|---:|---:|---:|---:|---:|
| FP32 | 2 | 8 | 0.09185155 | 0.145 | 125.41 |
| FP16 | 2 | 8 | 0.11375069 | 0.139 | 155.31 |
| FP16 | 4 | 4 | 0.05148910 | 0.197 | 70.30 |
| **FP16** | **8** | **2** | **0.02726956** | **0.297** | **37.23** |

**Adjudication: `T4_SYNTHETIC_4096_TARGET_CAPACITY=PASS_PROVISIONAL_INDEPENDENT_READBACK`.** The measurement code synchronizes CUDA on both sides of each timed optimizer step and includes forward/backward/optimizer. It uses two warmup plus four timed steps per configuration; limited duration and uniform full-length windows cannot prove full run duration. FP16/mb8/accum2 is **best measured candidate only**, **not yet the locked scientific config**.

## Why budget admission still HOLD

The real 2,048 TRAIN stories will form variable-length windows (most not full 256 targets). With a fixed 4,096 *actually scored* targets per step, more windows/microbatches may be required. Reported code proposes a further factor `max(1,256/mean_real_valid_targets)*1.10` above already reserved 25%; even that does not directly measure VAL, Drive checkpoint I/O, dataset transfer and Colab variability. Scientific cap is **5,400 seconds GPU**, not merely 37.23 seconds from synthetic extrapolation. The actual TRAIN window count and reuse ratio must be pinned **before** science. No runtime auto-increases, reduction of steps, or permission inferred from these results.

## Follow-on one integrated material preflight (no new micro-permits)

1. On Windows verify original exact T1 source SHA/manifest and the frozen T4 ZIP, run the prepared `t4_data_pack.py` via `Run-TTM-T4-Data-Pack-PS51.ps1` **one time** into project-local `_tmp/ttm_t4_data_pack_v1`. The resulting compressed token windows are private/reversible; never commit the NPZ to GitHub or issue TEST encoding.
2. Independently read `T4_PRIVATE_PACK_MANIFEST.json` and NPZ SHA, count real valid targets/windows, ratio of full windows, and 4,194,304 ÷ unique target reuse. Evaluate `t4_capacity_accept.py` once using this **actual** Drive capacity report + private manifest, document selected FP16/FP32 and microbatch, or HOLD if the 90-minute cap fails.
3. Archive/pin exact executable T4 source bundle on PR #12 (the ZIP SHA `cda8e692ce614c804bdffa1850abe6faeb0c51bccc0a8a0c1fbdee0145a0f524` currently exists as user conversation artifact, not fully committed as source). Run one integrated *synthetic* trainer+Drive/READY QA, review H1 baseline/CI and experiment permit. Only then adjudicate **ONE** science lock.

## Status

`T1_INDEPENDENT=PASS_SCOPED` · `T2_F32=PASS` · `T3_COLAB_RESUME=PASS` · `T4_GPU_SYNTHETIC_CAPACITY=PASS_PROVISIONAL` · `T4_PRIVATE_PACK=NOT_EXECUTED` · `T4_REAL_CAPACITY_CORRECTION=NOT_EXECUTED` · `T4_SCIENCE_LOCK=HOLD` · `T4_TRAIN=NOT_STARTED`.

**Bước thực hiện tiếp theo:** `TTM_T4_PRIVATE_TRAIN_VAL_PACK_AND_CAPACITY_ADJUSTED_INDEPENDENT_QA`. Do NOT rerun T1–T3 or the consumed GPU synthetic capacity run.
