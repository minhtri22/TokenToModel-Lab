# TTM T4 — Private TRAIN/VAL independent QA closure, trainer integrated CPU smoke and one GPU handoff

**2026-11-08** — `minhtri22/TokenToModel-Lab`, PR #12 DRAFT; `main` remains pinned. **No T4 TinyStories training performed; SCIENCE_LOCK=HOLD.**

## 1. Independent Windows private pack result accepted (technical scope)

Authoritative original Windows receipt: `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t4_privatepack_independent_qa_v1\T4_PRIVATE_PACK_AND_CAPACITY_INDEPENDENT_QA.json`. SHA256 independently computed from user-supplied original attachment **`c30b887c2ef906814827cb4963f1740b4a1aae58600a7fbae1c5e246cd477a1c`** and content compared to Windows read-only remote file. Exact JSON archived under `evidence/pilot/t4-privatepack/T4_PRIVATE_PACK_AND_CAPACITY_INDEPENDENT_QA.json`, Git blob **`2c8cf014260d7ef75e68b1c3223d9c54536fec71`**.

- The independent Python auditor loaded actual private NPZ and verified **exact eight TRAIN/VAL arrays** (`train_x/y/count/story_index`, `val_x/y/count/story_index`), dimensions and int16/int32 dtypes, in-vocab targets, correct -100 loss masks, input-to-target one-step shifts, within-story window joins and story-terminal EOS; no TEST array and `test_tokenization=0`.
- Original T1 source SHA/split/BPE pins preserved. TRAIN 2,048 stories, 2,691 windows, **498,287** valid next-token positions, mean **185.1679672984021** per window, 24.23% full 256-target windows; VAL 256 stories, 328 windows, 61,122 valid positions.
- Private `T4_PRIVATE_TRAIN_VAL_WINDOWS.npz` remains only on Windows, 1,186,107 bytes SHA256 **`184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913`**. Manifest SHA256 **`ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650`**. No reversible token data uploaded to public GitHub.
- `1024×4096=4,194,304` *training target exposures*, average reuse **8.417446170580408×** across the 498,287 distinct TRAIN target positions, which is **not** unique vocabulary size or number of independent examples.
- Tesla T4 synthetic benchmark SHA256 `c55a568496a888bc3abc95c0231a5ed17d3a6f366361571b6f89a4457d09f1ee` reviewed independently. Adjustment factor `256/185.1679672984021 ×1.10 = 1.5207813971`; provisional projected compute-only time for 1,024 steps: **FP16 mb8 = 56.62s**, FP16 mb4 = 106.91s, FP32 mb2 = 190.72s, FP16 mb2 = 236.19s. These projections **exclude measured full VAL/Drive overhead**. FP16 mb8 is a candidate, **not a locked science batch policy**. Original synthetic fixed accumulation `2` is NOT valid on real variable window lengths; T4 trainer must dynamically accumulate until precisely 4096 scored targets per step.

**Verdict:** `T4_PRIVATE_PACK_INDEPENDENT_QA=PASS_TECHNICAL_SCOPED`; `T4_CAPACITY_ADJUSTED=PASS_PROVISIONAL_ONLY`. This does not issue scientific authority or establish overfitting/real H1 performance.

## 2. Additional source-level integrated synthetic CPU trainer QA

Original frozen T4 trainer `t4_train_science.py`, H1 evaluator `t4_eval.py`, P02 source exact SHA256 `e0fcac285918b66b13c8f694e6d625a0691c9b59221b43043e63f46b25ddcc07` exercised on **43 purely synthetic variable-length windows**, mean 192.186 valid targets.

- Actual `train_one_step(..., microbatch_windows=8)`: **4096 scored targets per optimizer step**. First step used 23 windows, second 20 windows. This verifies accumulation must be **dynamic**, rather than fixed 2 based on full synthetic windows.
- Actual P02 small-dimension diagnostic + AdamW + scheduler + sampler; uninterrupted second CPU optimizer step compared to step1 saved checkpoint + `weights_only=True,map_location='cpu'` restored second step: **loss/weights/optimizer/sampler exactly equal**, READY-last checkpoint and SHA readback PASS. This is an integration test of original trainer code paths, not the full frozen model/GPU timing.
- Same test exercised TRAIN-only bigram evaluator, synthetic VAL story scores/bootstrap 1000 and fail-closed missing science lock. No TinyStories, TEST or GPU. Receipt SHA256 `a2060b48c28adc766cd20d97ff87a536dad4dc20cb0bf8a151bff1a164da444f`, byte-exact Git blob `0eb868582f940fd1cc9a6838e727023ec763d55b` at `evidence/pilot/t4-trainer/T4_LOCAL_SYNTHETIC_TRAINER_INTEGRATION_QA.json`.

**Verdict:** `T4_CPU_SYNTHETIC_TRAINER_INTEGRATION=PASS`. Not an actual Tesla T4 trainer/Drive readiness PASS.

## 3. Single remaining technical integration handoff before the scientific decision

A **new zero-science Colab integration notebook** is prepared as user-visible conversation artifact:

- `TTM_T4_Synthetic_Trainer_GPU_Drive_Integration_20261108_v1.ipynb` SHA256 **`3c2ff67f7a2b4e94d62623d59ae5299965894479d92af0b5a49d104f18ad8ee4`**.
- ZIP with notebook, worker source, CPU integration source+receipt: `TTM_T4_SYNTHETIC_TRAINER_GPU_INTEGRATION_V1_20261108.zip`, SHA256 **`a3f122bfbe0e5c59bfe7a74fb140c782dcb0a19b2036cb20ac906e6109657a94`**.
- Notebook source cells AST PASS and five embedded scripts individually SHA-verified vs the frozen T4 bundle; worker CLI static PASS; **GPU notebook has NOT yet been run**. Runtime demands Tesla T4, torch `2.14.1+cu130`; uses only generated variable-length synthetic token IDs, exact full P02 3.75M parameter architecture, 4096 non-PAD scored targets per step, FP16 mb8 candidate, true GPU step1 checkpoint to Drive, readback/restore then GPU step2; independently computes synthetic bigram/VAL evaluator without real data.
- It writes a distinct one-shot folder `MyDrive/TTM/ttm-small-pilot/t4_trainer_gpu_integration_synthetic_20261108_v1/` with step1 checkpoint, `READY.json` and `T4_SYNTHETIC_TRAINER_INTEGRATION_REPORT.json`; user must flush/unmount and independent Google Drive connector must SHA-verify the actual file and checkpoint before approving the GPU trainer integration. No rerun on partial failure, no accessing private TRAIN NPZ/TEST.
- **Limitation:** notebook is source artifact ready for user to run, its source has not yet been merged/archived into GitHub. The core T4 executable bundle ZIP SHA256 `cda8e692ce614c804bdffa1850abe6faeb0c51bccc0a8a0c1fbdee0145a0f524` also remains a conversation artifact pending source archival. Public GitHub currently has docs/receipts only for T4. Preserve these gaps before PR merge.

## 4. One final integrated prereg science decision only

After GPU synthetic trainer/Drive exact readback, archive complete byte-pinned T4 sources into PR #12, verify H1 bigram Add-0.1, >=5% relative NLL improvement and story-bootstrap 95% lower CI>0 on VAL, 2048/256/64 data scope, fixed seed20261108, 1024×4096 budget and 90-minute cap. Evaluate rights and T5 trained checkpoint export responsibility. Then issue **one explicit scientific one-shot decision**. No micro-permits or further T1–T3 reruns. `lineage.md` append only for scientific outcomes, not engineering QA.

**State:** `T1/T2/T3=PASS_SCOPED`; `T4_PRIVATE_PACK_INDEPENDENT=PASS`; `T4_SYNTHETIC_CAPACITY=PASS_PROVISIONAL`; `T4_CPU_TRAINER_INTEGRATION=PASS`; `T4_FULL_GPU_TRAINER_INTEGRATION=NOT_EXECUTED`; `T4_SCIENCE_LOCK=HOLD`; `T4_TRAIN=NOT_STARTED`.

**Bước thực hiện tiếp theo:** `TTM_T4_GPU_SYNTHETIC_TRAINER_DRIVE_INTEGRATION_AND_ONE_SHOT_SCIENCE_GATE_REVIEW`.
