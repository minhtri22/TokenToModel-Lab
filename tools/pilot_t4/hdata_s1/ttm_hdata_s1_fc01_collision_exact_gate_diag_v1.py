#!/usr/bin/env python3
"""H-DATA-S1 owner Colab diagnostic for FC01 namespace collision.

No model forward, no optimizer update, no science, no resume, no FINAL.
No changes to frozen checkpoint/source/run root. Writes only temporary
public-safe AES ciphertext (not secret key/plain mapping), auto-removed.
Use in the same Colab runtime after drive.mount('/content/drive').
"""
from __future__ import annotations
import hashlib, importlib.util, json, pathlib, shutil, sys, tempfile, traceback, types, zipfile

H_REPO = pathlib.Path("/content/TTM_HDATA_S1_SCIENCE_FROZEN")
H_ROOT = pathlib.Path("/content/drive/MyDrive/TTM/ttm-small-pilot/ttm_small4m_h_data_s1_20261113/science_one_shot_v1")
H_BASE = pathlib.Path("/content/drive/MyDrive/TTM/ttm-small-pilot")
H_INPUT = H_REPO / "tools/pilot_t4"
H_SCRIPT = H_INPUT / "hdata_s1/ttm_hdata_s1_two_arm_science_runner_candidate_v1.py"
H_QA = H_INPUT / "hdata_s1/ttm_hdata_s1_native_t4_h0_h1_resume_qa_v1.py"
H_SAMPLER = H_INPUT / "hdata_s1/ttm_hdata_s1_real_metadata_preexec_v1.py"
H_BASE_MODULE = H_INPUT / "prompt_conditioning_2x2/ttm_2x2_colab_runner_candidate.py"
H_P02 = H_INPUT / "integrated/p02_source_exact.py"
H_LOCK = H_REPO / "artifacts/qa/ttm-small4m-h-data-s1/preexec_real_train/TTM_HDATA_S1_OWNER_SCIENCE_ONE_SHOT_GO_LOCK_20261113.json"
H_RIGHTS = H_REPO / "artifacts/qa/ttm-small4m-h-data-s1/preexec_real_train/TTM_HDATA_S1_NEW_OWNER_RIGHTS_INTERNAL_CDLA_SCOPED_20261113.json"
H_COMMITMENT = H_REPO / "docs/research/ttm-small4m-h-data-s1/TTM_HDATA_S1_NEW_FINAL24_PUBLIC_SHA_COMMITMENT_20261113.json"
H_OWNER = H_BASE / "ttm_small4m_h_data_s1_20261113/owner_private"
H_QA_RECEIPT = H_OWNER / "TTM_HDATA_S1_T4_NATIVE_RESUME_QA_RECEIPT_20261113.json"
H_ZIP = H_OWNER / "TTM_HDATA_S1_OWNER_PRIVATE_ESCROW_BACKUP_DO_NOT_GITHUB.zip"

H_SHA = {
 "runner":"eae016e92adc862e71d98920844ebd7c36bacbc3c9157c5a5e33d31aa77ded28",
 "lock":"85e744a3da8d0e417079f726d95f059ad569a5f13e592ee56c1982dbce0aa540",
 "qa":"7db0f999934036fc4f87beda9cd5a131377147d7307e9de5ac3a52b547882e62",
 "qa_receipt":"c93fe27e275cd7a1bcd80f369b2a54667a3da3a5b6a942482f80c0b80c38af8c",
 "escrow_zip":"c5c5d6eae6ce38d892348878ae200d5bbcd42406b53f7b0c43e8876a145d48d4",
 "escrow":"de0562cd4a9584ca8128e505b14e3d04ae35793b72f7d8a2b4d4f6eb0176cc7d",
 "pack":"184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913",
 "parent":"cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b",
 "bpe":"cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc",
 "manifest":"ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650",
}

def need(ok,code):
    if not ok: raise RuntimeError("H_DATA_S1_TRIAGE_HOLD:"+code)

def sha(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def pinned(name,digest):
    matches=[]
    for p in H_BASE.rglob(name):
        if p.is_file() and not p.is_symlink() and sha(p)==digest:
            matches.append(p)
    need(bool(matches),"PINNED_SOURCE_MISSING:"+name)
    return sorted(matches)[0]

def state_inventory():
    print("HDATA_S1_CANONICAL_ROOT="+str(H_ROOT))
    print("HDATA_S1_RUN_ROOT_EXISTS="+str(H_ROOT.exists()))
    print("HDATA_S1_RUN_ROOT_IS_DIR="+str(H_ROOT.is_dir()))
    if H_ROOT.is_dir():
        print("HDATA_S1_ROOT_CHILDREN="+json.dumps(sorted(p.name for p in H_ROOT.iterdir())))
        for arm in ("H0","H1"):
            d=H_ROOT/("ARM_"+arm)
            print("HDATA_S1_"+arm+"_BEGIN="+str(len(list(d.glob("STEP_BEGIN_*.json")))))
            print("HDATA_S1_"+arm+"_DONE="+str(len(list(d.glob("STEP_DONE_*.json")))))
            print("HDATA_S1_"+arm+"_READY="+json.dumps(sorted(p.parent.name for p in d.glob("checkpoint_*/READY.json"))))
    try:
        print("HDATA_S1_DRIVE_FREE_GIB=%.3f"%(shutil.disk_usage(H_ROOT.parent).free/1024**3))
    except OSError as exc:
        print("HDATA_S1_DISK_USAGE_ERROR="+type(exc).__name__+":"+str(exc))

def run():
    print("HDATA_S1_NESTED_FC01_GLOBALS=IGNORED")
    print("HDATA_S1_DIAGNOSTIC=READONLY_PREEXEC_NO_MODEL_FORWARD")
    state_inventory()
    need(H_SCRIPT.is_file() and sha(H_SCRIPT)==H_SHA["runner"],"H_DATA_RUNNER_SHA")
    need(H_LOCK.is_file() and sha(H_LOCK)==H_SHA["lock"],"H_DATA_GO_LOCK_SHA")
    need(sha(H_QA)==H_SHA["qa"],"H_DATA_NATIVE_QA_SHA")
    need(sha(H_QA_RECEIPT)==H_SHA["qa_receipt"],"H_DATA_NATIVE_QA_RECEIPT_SHA")
    need(sha(H_ZIP)==H_SHA["escrow_zip"],"H_DATA_OWNER_ESCROW_ZIP_SHA")
    h_lock=json.loads(H_LOCK.read_text("utf-8"))
    need(h_lock.get("science_runner_sha256")==H_SHA["runner"],"GO_LOCK_RUNNER_MISMATCH")
    print("HDATA_S1_RUNNER_SHA_PIN=PASS")
    print("HDATA_S1_LOCK_SHA_PIN=PASS")

    # Always import the exact module by an absolute path, NEVER a notebook RUNNER variable.
    spec=importlib.util.spec_from_file_location("hdata_s1_exact_science_gate_diag",H_SCRIPT)
    h_mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=h_mod
    spec.loader.exec_module(h_mod)
    need(pathlib.Path(h_mod.__file__).resolve()==H_SCRIPT.resolve(),"WRONG_MODULE_IMPORTED")
    print("HDATA_S1_IMPORTED_MODULE="+str(h_mod.__file__))

    h_pack=pinned("T4_PRIVATE_TRAIN_VAL_WINDOWS.npz",H_SHA["pack"])
    h_manifest=pinned("T4_PRIVATE_PACK_MANIFEST.json",H_SHA["manifest"])
    h_parent=pinned("checkpoint.pt",H_SHA["parent"])
    h_bpe=pinned("T1_BPE2048_REAL_TRAIN_MANIFEST.json",H_SHA["bpe"])

    with zipfile.ZipFile(H_ZIP) as z:
        name="TTM_HDATA_S1_ENCRYPTED_BLIND_ESCROW_PUBLIC_SAFE.json"
        need(name in z.namelist(),"ESCROW_CIPHERTEXT_NOT_FOUND")
        cipher=z.read(name)
    need(hashlib.sha256(cipher).hexdigest()==H_SHA["escrow"],"ESCROW_CIPHERTEXT_DRIFT")
    with tempfile.TemporaryDirectory(prefix="hdata_s1_gate_diagnostic_only_") as t:
        h_escrow=pathlib.Path(t)/"AES_ENCRYPTED_ONLY.json"
        h_escrow.write_bytes(cipher)
        args=types.SimpleNamespace(lock=str(H_LOCK),lock_sha=H_SHA["lock"],
            qa_receipt=str(H_QA_RECEIPT),rights_receipt=str(H_RIGHTS),
            escrow=str(h_escrow),escrow_sha=H_SHA["escrow"],
            runner_qa=str(H_QA),sampler=str(H_SAMPLER),
            base=str(H_BASE_MODULE),p02=str(H_P02),pack=str(h_pack),
            manifest=str(h_manifest),parent=str(h_parent),bpe=str(h_bpe),
            commitment=str(H_COMMITMENT),root=str(H_ROOT))
        h_mod.gate(args)
    print("HDATA_S1_EXACT_SCIENCE_GATE=PASS_NO_MODEL_FORWARD")
    print("HDATA_S1_CAUSE_OF_ORIGINAL_EXIT_CODE_1=NOT_YET_IDENTIFIED")
    print("HDATA_S1_DO_NOT_RERUN_OR_RESUME_UNTIL_ORIGINAL_FAILURE_ADJUDICATION")

if __name__=="__main__":
    try:
        run()
    except Exception as exc:
        print("HDATA_S1_EXACT_SCIENCE_GATE=HOLD")
        print("HDATA_S1_ERROR_TYPE="+type(exc).__name__)
        print("HDATA_S1_ERROR_MESSAGE="+str(exc))
        traceback.print_exc(limit=8)
    finally:
        print("HDATA_S1_SCIENCE_DISPATCH_BY_DIAGNOSTIC=NONE")
        print("HDATA_S1_NEW_FINAL=SEALED")
