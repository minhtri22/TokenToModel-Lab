#!/usr/bin/env python3
"""Owner H-DATA-S1 NEW FINAL24 release source QA only. No FINAL/GPU/secret reads."""
from __future__ import annotations
import ast,hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
HD=ROOT/"tools/pilot_t4/hdata_s1"
GEN=HD/"ttm_hdata_s1_new_final24_blind_generation_candidate_source_only_v1.py"
PERMIT=ROOT/"artifacts/qa/ttm-small4m-h-data-s1/science_postrun/TTM_HDATA_S1_OWNER_NEW_FINAL24_ONE_SHOT_INFERENCE_GO_PERMIT_20261114.json"
NB=HD/"TTM_HDATA_S1_OWNER_NEW_FINAL24_ONE_SHOT_COLAB_20261114.ipynb"
SCIENCE=ROOT/"artifacts/qa/ttm-small4m-h-data-s1/science_postrun/TTM_HDATA_S1_INDEPENDENT_READY_LAST_VAL_FREEZE_20261114.json"
EXPECTED_GENERATOR_SHA="7953d33fa592a8890a185cedf490d7af2df9514e025395f00a1996c7bf784363"
EXPECTED_PERMIT_SHA="242a0925320e9c4aeb716fca4324cdce12d384f52322589f2e403ae464702581"
EXPECTED_FROZEN_REF="9ed7116b53eeb77ddbcc4b5728c81a6a971f8dfe"
EXPECTED_OWNER_LAST_SHA="e30a2281580b1f6ea33856577f0a244cd02e226dc8a3db00d207a8fe13cce4b5"

def dig(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(b,s):
 if not b:raise RuntimeError("H_DATA_S1_OWNER_FINAL_RELEASE_SOURCE_HOLD:"+s)
def run():
 need(dig(GEN)==EXPECTED_GENERATOR_SHA,"GENERATOR_SHA_DRIFT")
 need(dig(PERMIT)==EXPECTED_PERMIT_SHA,"OWNER_PERMIT_SHA_DRIFT")
 src=GEN.read_text("utf8")
 compile(src,str(GEN),"exec")
 permit=json.loads(PERMIT.read_bytes())
 receipt=json.loads(SCIENCE.read_bytes())
 need(permit["schema"]=="ttm.hdata_s1.owner_final24_generation_permit.v1" and
      permit["authorization"]=="GO_HDATA_S1_NEW_FINAL24_ONE_SHOT_OWNER_INFERENCE" and
      permit["explicit_owner_decision"] is True,"OWNER_GO_NOT_SCOPE_LOCKED")
 need(permit["generator_source_sha256"]==EXPECTED_GENERATOR_SHA and
      permit["science_lock_sha256"]==receipt["custody"]["science_lock_sha256"] and
      permit["science_owner_ready_last_receipt_sha256"]==EXPECTED_OWNER_LAST_SHA and
      permit["h0_checkpoint_sha256"]==receipt["arms"][0]["last_checkpoint_sha256_independently_verified"] and
      permit["h1_checkpoint_sha256"]==receipt["arms"][1]["last_checkpoint_sha256_independently_verified"],
      "OWNER_GO_SCIENCE_CHAIN")
 need(permit["final_owner_prompt_sha256"]=="b129a5c52520a25f1c40de950471622320abfa6b5414d0b16e0111ed96adc680" and
      permit["AES_escrow_sha256"]=="de0562cd4a9584ca8128e505b14e3d04ae35793b72f7d8a2b4d4f6eb0176cc7d" and
      permit["single_run_root"]=="/content/drive/MyDrive/TTM/ttm-small-pilot/ttm_small4m_h_data_s1_20261113/new_final24_blind_generation_once_v1",
      "OWNER_GO_FINAL_AES_ROOT")
 need(permit["unblind_authorized"] is False and
      permit["scoring_authorized"] is False and permit["no_training"] is True and
      permit["owner_dispatch_executed_by_this_record"] is False,
      "NO_RATER_NO_UNBLIND_NO_TRAIN")
 need(src.index("check_permit(args, selfsha)") <
      src.index('os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"') <
      src.index("    import torch",src.index("def generate_once(args):")),
      "PERMIT_BEFORE_TORCH_CUBLAS_GUARD")
 nb=json.loads(NB.read_text("utf8"))
 need(nb["nbformat"]==4 and len(nb["cells"])==2,"COLAB_NOTEBOOK_STRUCT")
 cell="".join(nb["cells"][1]["source"])
 compile(cell,str(NB)+"#CELL2","exec")
 need("HDATA_FINAL24_RUN_NOW = False" in cell and
      EXPECTED_FROZEN_REF in cell and EXPECTED_GENERATOR_SHA in cell and
      EXPECTED_PERMIT_SHA in cell,"COLAB_MANUAL_PINS_AND_FAIL_CLOSED")
 need('not final_root.exists()' in cell and
      '"--mode", "generate"' in cell and
      "FINAL_ONE_SHOT_ALREADY_EXISTS_NO_REPLAY" in cell and
      "H_DATA_S1_FINAL24_ONE_SHOT_FAILED_DO_NOT_REPLAY" in cell,
      "ONE_SHOT_NO_OVERWRITE_POLICY")
 test=subprocess.run([sys.executable,str(GEN),"--mode","source-only"],
                     text=True,capture_output=True,timeout=20,check=True)
 obj=json.loads(test.stdout)
 need(obj["status"]=="SOURCE_ONLY_FINAL_OWNER_RELEASE_NOT_GRANTED" and
      obj["optimizer_updates"]==0 and obj["model_import_or_forward"] is False,
      "SOURCE_ONLY_RUNNER_GATE")
 bad=subprocess.run([sys.executable,str(GEN),"--mode","generate"],
                    text=True,capture_output=True,timeout=20)
 need(bad.returncode!=0 and "EXPLICIT_NEW_FINAL24_OWNER_PERMIT_NOT_SUPPLIED" in bad.stderr,
      "NEGATIVE_NO_PERMIT_MUST_FAIL_BEFORE_TORCH")
 return {"schema":"ttm.hdata_s1.owner_final24_one_shot_release_source_qa.v1",
         "status":"PASS_OWNER_GO_PERMIT_AND_COLAB_SOURCE_NO_INFERENCE",
         "permit_sha256":EXPECTED_PERMIT_SHA,
         "candidate_sha256":EXPECTED_GENERATOR_SHA,
         "manual_notebook_default":"FAIL_CLOSED_FALSE",
         "no_owner_model_forward":True,
         "no_private_prompt_or_AES_read":True,
         "no_trainer_or_unblind":True,
         "negative_no_permit":"PASS",
         "run_id":permit["run_id"]}
if __name__=="__main__":
 print(json.dumps(run(),ensure_ascii=False,sort_keys=True,indent=2))
