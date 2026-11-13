# FC01 V2 — Một quyết định về quyền dữ liệu, Colab FP32 và Drive zero-step

**Operation:** `TTM_SMALL4M_FC01_T4_FP32_DRIVE_RESUME_RIGHTS_SINGLE_INTEGRATED_SCIENCE_RELEASE_GO_HOLD_ZERO_TRAIN_STEPS`
**Ngày:** 13/11/2026 · **Quyết định owner khoa học: `HOLD_PREEXEC`**. Không optimizer step, inference, GPU training, D1/TEST.

## 1. Bằng chứng nguồn đã có

- FC01 V2 Windows source QA và T1 BPE thật PASS; 384 families = TRAIN 256 / VAL 64 / EVAL 64; 512 episodes/arm; B/C bytes identical.
- Corpus private SHA-256 `becc0408880aaed8bd5eb6fdf3997e62d5131c187a48331a03ae37d41aaa1aa3`; parent checkpoint step1024 `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`; T1 BPE `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc`.
- Independent separate-code self-authored QA 16/16 PASS; runner `--mode audit` PASS source-only. Chưa phải test load checkpoint/optimizer trên Colab.

## 2. Source rights

- TinyStories `roneneldan/TinyStories`: https://huggingface.co/datasets/roneneldan/TinyStories
- Dataset license declaration: `CDLA-Sharing-1.0`; official text https://cdla.dev/sharing-1-0/ ; TRAIN upstream SHA-256 `c5cf5e22ff13614e830afbe61a99fbcbe8bcb7dd72252b989fa1117a368d401f`.
- CDLA-Sharing-1.0 grants Use and Publication under conditions, with special duties for publishing Data or Enhanced Data; computational Results are defined separately. **Owner acceptance: NOT_RECEIVED**. No assistant self-signature or sharing raw private TRAIN/EVAL.

## 3. Cloud runtime and custody

- Public Google Colab FAQ: https://research.google.com/colaboratory/faq.html ; free GPU access and device types are dynamic, not guaranteed. A connected Google Drive account is not a running Colab Python kernel.
- Searched connected Drive for FC01 notebook outputs: none found; prior T4 folders from older studies do not establish FC01 runtime readiness.
- `COLAB_FREE_T4=NOT_VERIFIED`, `COLAB_FP32_MODEL_LOAD=NOT_EXECUTED`, `COLAB_DRIVE_SAVE_RELOAD_SHA=NOT_EXECUTED`, `FC01_TRAIN_STEP64_RESUME=NOT_EXECUTED`.
- Colab one-packet notebook added to research branch: `tools/pilot_t4/fc01/TTM_FC01_T4_FP32_DRIVE_ZERO_STEP_RIGHTS_ONEPACKET_20261113.ipynb`. Owner rights and Free T4 flags default false; no science GO lock is created.

## 4. Scoped Drive prep and one handoff

- Private project root: https://drive.google.com/drive/folders/1F2zEU_nS36pJDIkdiznxOp4LUPG8UHxv
- Upload exact **seven files** to https://drive.google.com/drive/folders/1U6JQ6I0ZJumRlnsyD3XB3-wsO2tznDwA : `FC01_OWNER_PRIVATE_DATA.json`, `T4_PRIVATE_TRAIN_VAL_WINDOWS.npz`, `T4_PRIVATE_PACK_MANIFEST.json`, `CF1_STEP1024_PINNED.pt`, `T1_BPE2048_REAL_TRAIN_MANIFEST.json`, `p02_exact.py`, `fc01_train_eval_once.py`.
- The first six already exist under local Windows `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\TTM_FC01_SOURCE_BUNDLE_20261113_v2`; the runner file is under `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\fc01_onepacket_20261113_v2`.
- Read receipts at https://drive.google.com/drive/folders/1K5TpN299jEDFUeBu3n2kwKOwkaEkEzea . No private bytes are committed publicly.
- Open notebook from GitHub in the Colab UI, verify the official license personally, set the two `OWNER_*` values to true only with informed approval, and run **once** in a Free T4 runtime if available. It pins SHA, loads exact P02 checkpoint, tests FP32 and Drive snapshot+readback of model/optimizer/RNG/cursors with **zero optimizer steps, zero model forward/backward, zero inference**.
- **Limit:** the test snapshot is explicitly `NOT_SCIENCE_CHECKPOINT`. Save–reload of step0 components does not demonstrate the actual FC01 training runner's step64 resume. The 3 GPU-hour budget is a cap, not a performance guarantee.

## 5. Single science decision and preserved gates

**`FC01_SCIENCE=HOLD_PREEXEC`** until owner rights attestation and dated Colab Free T4 zero-step receipt can be verified. One decision for A/B/C; no micro-permits.

`FC01_V2_SOURCE_QA=PASS` · `RIGHTS_PUBLIC_LICENSE=VERIFIED` · `RIGHTS_OWNER=NOT_ATTESTED` · `COLAB_ZERO_STEP=NOT_EXECUTED` · `SCIENCE_GO=NOT_GRANTED` · `TRAINING_STEPS=0` · `D1_CONFIRMATORY=HOLD` · `TEST_Q1Q2=SEALED` · `DEV32=CLOSED` · `LINEAGE=UNCHANGED` · `MAIN=UNCHANGED`.

**Bước thực hiện tiếp theo:** `TTM_FC01_OWNER_COLAB_ONE_NOTEBOOK_ZERO_STEP_RECEIPT_RETURN`; the user runs the one notebook and returns the receipt SHA or output. Never use the step0 QA snapshot as a training resume.

**Canonical safe receipt:** `artifacts/research/ttm-small4m-fact-conditioning/TTM_FC01_T4_FP32_DRIVE_RESUME_RIGHTS_INTEGRATED_PREEXEC_OWNER_HOLD_20261113.json`.
