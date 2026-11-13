# H-DATA-S1 — Owner Colab T4 native resume QA, ONE PACKET, NO SCIENCE TRAIN

**Operation:** `TTM_HDATA_S1_OWNER_RIGHTS_NATIVE_T4_TRAINER_RESUME_AES_ESCROW_SINGLE_PACKET_FINAL_RELEASE_NO_AUTO_TRAIN`  
**Branch:** `research/ttm-small4m-h-data-s1-matched-budget-prereg-20261113`  
**Pinned source snapshot:** `fbb57179318c6d0f42215647bc1087c6de093c5e`  
**Current release:** `HOLD_NO_AUTO_TRAIN`. This is a manual Colab T4 QA cell, not a command to train 128 science steps.

## What is already frozen

- Real TRAIN sampler matched-budget metadata: `PASS` on 128 steps, 4096 labels/step; 2928 paired windows/arm, plan SHA `bcb354d29540e3a348b76173cdad1a6e2832dc81f995c717b68be6926d456591`.
- Source-only GitHub Actions `43422638525`: `PASS`, Python 3.12 AST, SHA256, Git blobs, secret/execution guards; this is **not** T4 parity.
- Owner-private AES-256-GCM ciphertext SHA `de0562cd4a9584ca8128e505b14e3d04ae35793b72f7d8a2b4d4f6eb0176cc7d`; owner-private ZIP SHA `c5c5d6eae6ce38d892348878ae200d5bbcd42406b53f7b0c43e8876a145d48d4`. ZIP Drive exact-byte readback PASS; never publish key/clear map.
- H-DATA new owner internal research rights receipt: SHA `f1ae54c94d8c6a4a55febd4544b7c474ae73f060e8e9f64b426b5ca91740de2f`. Source card declares `cdla-sharing-1.0`; no raw dataset redistribution.
- SHA of QA runner `7db0f999934036fc4f87beda9cd5a131377147d7307e9de5ac3a52b547882e62`; SHA of training runner **candidate** `1874aebf904a57782acad963838db86f01556d2fe287927e616574b5700985a7`. The candidate is locked by an owner GO receipt not yet available.

## Colab T4 manual QA cell (once only)

The following code **does not run itself**. Owner runs it in a new Colab T4 with Drive mounted and approved. It runs **8 non-science QA optimizer updates** (4 per arm: two uninterrupted, one pre-checkpoint, one after resume) using real TRAIN, solely to verify exact-state parity. **Science optimizer updates remain 0**; no FINAL, NEXT24, TEST/Q1/Q2/OOD are opened.

```python
from google.colab import drive
drive.mount('/content/drive')

import hashlib, json, pathlib, subprocess, tempfile, zipfile, os
BASE=pathlib.Path('/content/drive/MyDrive/TTM/ttm-small-pilot')
REPO=pathlib.Path('/content/TTM_HDATA_S1_PREEXEC_FROZEN')
COMMIT='fbb57179318c6d0f42215647bc1087c6de093c5e'
BRANCH='research/ttm-small4m-h-data-s1-matched-budget-prereg-20261113'
if REPO.exists(): raise RuntimeError('FROZEN_REPO_ALREADY_EXISTS_NO_OVERWRITE')
subprocess.run(['git','clone','--quiet','--single-branch','--branch',BRANCH,
 'https://github.com/minhtri22/TokenToModel-Lab.git',str(REPO)],check=True)
subprocess.run(['git','checkout','--detach',COMMIT],cwd=REPO,check=True)

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def pick(name,expected):
    found=sorted(p for p in BASE.rglob(name) if p.is_file() and sha(p)==expected)
    if not found: raise RuntimeError('SOURCE_PIN_NOT_FOUND:'+name)
    return found[0]

pack=pick('T4_PRIVATE_TRAIN_VAL_WINDOWS.npz','184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913')
manifest=pick('T4_PRIVATE_PACK_MANIFEST.json','ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650')
parent=pick('checkpoint.pt','cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b')
bpe=pick('T1_BPE2048_REAL_TRAIN_MANIFEST.json','cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc')
owner=BASE/'ttm_small4m_h_data_s1_20261113'/'owner_private'
z=owner/'TTM_HDATA_S1_OWNER_PRIVATE_ESCROW_BACKUP_DO_NOT_GITHUB.zip'
assert sha(z)=='c5c5d6eae6ce38d892348878ae200d5bbcd42406b53f7b0c43e8876a145d48d4'
src=REPO/'tools/pilot_t4'
h=src/'hdata_s1'
commitment=REPO/'docs/research/ttm-small4m-h-data-s1/TTM_HDATA_S1_NEW_FINAL24_PUBLIC_SHA_COMMITMENT_20261113.json'
qa=h/'ttm_hdata_s1_native_t4_h0_h1_resume_qa_v1.py'
assert sha(qa)=='7db0f999934036fc4f87beda9cd5a131377147d7307e9de5ac3a52b547882e62'
assert sha(commitment)=='6c8c21c406b4bc30171244142c4226460a6735164f88fd425db7afa070a6f4f3'
subprocess.run(['python',str(qa),'--mode','source-qa'],check=True)
out=owner/'TTM_HDATA_S1_T4_NATIVE_RESUME_QA_RECEIPT_20261113.json'
if out.exists(): raise RuntimeError('RECEIPT_ALREADY_EXISTS_NO_RERUN')
with tempfile.TemporaryDirectory(prefix='hdata_s1_owner_only_') as td:
    with zipfile.ZipFile(z) as zz:
        wanted=['TTM_HDATA_S1_OWNER_AES_KEY_PRIVATE_DO_NOT_GITHUB.json',
                'TTM_HDATA_S1_ENCRYPTED_BLIND_ESCROW_PUBLIC_SAFE.json']
        assert set(zz.namelist())==set(wanted+['README_OWNER_PRIVATE.txt'])
        for name in wanted:
            pathlib.Path(td,name).write_bytes(zz.read(name))
    escrow=pathlib.Path(td,wanted[1])
    assert sha(escrow)=='de0562cd4a9584ca8128e505b14e3d04ae35793b72f7d8a2b4d4f6eb0176cc7d'
    cmd=['python',str(qa),'--mode','t4-resume-qa',
         '--pack',str(pack),'--manifest',str(manifest),
         '--parent',str(parent),'--bpe',str(bpe),
         '--commitment',str(commitment),
         '--escrow',str(escrow),'--escrow-sha',sha(escrow),
         '--sampler',str(h/'ttm_hdata_s1_real_metadata_preexec_v1.py'),
         '--base',str(src/'prompt_conditioning_2x2/ttm_2x2_colab_runner_candidate.py'),
         '--p02',str(src/'integrated/p02_source_exact.py'),
         '--out',str(out),
         '--self-sha','7db0f999934036fc4f87beda9cd5a131377147d7307e9de5ac3a52b547882e62',
         '--allow-eight-nonscience-qa-updates']
    subprocess.run(cmd,check=True)
receipt=json.loads(out.read_bytes())
assert receipt['status']=='PASS_NATIVE_T4_FULL_INTERRUPTED_RESUME_EXACT_H0_H1'
assert receipt['qa_optimizer_updates']==8 and receipt['science_optimizer_updates']==0
print('HDATA_S1_T4_NATIVE_QA=PASS_SCOPED')
print('HDATA_S1_T4_QA_RECEIPT_SHA256='+sha(out))
print('HDATA_S1_SCIENCE=HOLD_NO_AUTO_TRAIN')
```

## Required independent readback

Review the T4 QA receipt (SHA and both H0/H1 direct-vs-resume exact model, AdamW, scheduler, GradScaler and RNG), the rights scope and parent pins. Do not rekey escrow. This QA is **not a science release**. A production GO lock must only be produced after independent readback confirms all gates, with a separate future one-shot dispatch.

If T4 is unavailable or runtime Torch differs from exactly `2.14.1+cu130`, stop and record `HOLD_T4_RUNTIME`; do not silently substitute CPU, different precision or another CUDA version. No FINAL prompt text is opened during QA.
