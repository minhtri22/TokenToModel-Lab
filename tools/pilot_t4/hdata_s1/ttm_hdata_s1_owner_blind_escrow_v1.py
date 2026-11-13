#!/usr/bin/env python3
"""H-DATA-S1 owner-only HF01..HF24 AES-256-GCM blind escrow.
No FINAL prompt content, training, model-forward, old NEXT24 or unblinding.
CREATE ONCE in a private owner directory. Never commit the AES key.
"""
from __future__ import annotations
import argparse, base64, collections, hashlib, json, os, pathlib, secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

RUN_ID="TTM_SMALL4M_HDATA_S1_MATCHED_BUDGET_FRESH_FINAL_V1"
COMMITMENT_SHA="6c8c21c406b4bc30171244142c4226460a6735164f88fd425db7afa070a6f4f3"
AAD=("TTM_HDATA_S1_HF01_HF24_AES256GCM_V1|"+RUN_ID+"|"+COMMITMENT_SHA).encode()
KEY_NAME="TTM_HDATA_S1_OWNER_AES_KEY_PRIVATE_DO_NOT_GITHUB.json"
ESCROW_NAME="TTM_HDATA_S1_ENCRYPTED_BLIND_ESCROW_PUBLIC_SAFE.json"

def canonical(obj):
    return json.dumps(obj,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode("utf-8")
def sha(data):
    return hashlib.sha256(data).hexdigest()
def need(cond,why):
    if not cond: raise RuntimeError("H_DATA_S1_ESCROW_HOLD:"+why)
def put_new(path,content):
    fd=os.open(str(path),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,"wb") as f:
        f.write(content);f.flush();os.fsync(f.fileno())
def index_from_public(path):
    path=pathlib.Path(path)
    need(path.is_file() and not path.is_symlink(),"MISSING_PUBLIC_COMMITMENT")
    raw=path.read_bytes()
    need(sha(raw)==COMMITMENT_SHA,"PUBLIC_COMMITMENT_SHA_DRIFT")
    obj=json.loads(raw)
    need(obj.get("run_id")==RUN_ID and obj.get("final_count")==24,"PUBLIC_COMMITMENT_SCOPE")
    entries=obj["committed_prompt_hashes"]
    need(len(entries)==24 and [e["id"] for e in entries]==["HF%02d"%i for i in range(1,25)],"HF_ORDER")
    by=collections.defaultdict(list)
    seen=set()
    for e in entries:
        need(e.get("cohort")=="BLIND_FINAL" and e["stratum"] in
             ("object_custody","social_relation","causal_obstacle","temporal_rule"),"STRATUM")
        h=e["prompt_utf8_sha256"]
        need(isinstance(h,str) and len(h)==64 and all(x in "0123456789abcdef" for x in h),"HASH")
        need(h not in seen,"REPEATED_PROMPT");seen.add(h)
        by[e["stratum"]].append(e["id"])
    need(len(by)==4 and all(len(v)==6 for v in by.values()),"STRATUM_COUNTS")
    return entries,by

def validate_pairs(pairs,entries):
    need(len(pairs)==24,"PAIR_COUNT")
    expected={e["id"]:e["stratum"] for e in entries}
    per=collections.defaultdict(list)
    for i,p in enumerate(pairs,1):
        pid="HF%02d"%i
        need(p.get("prompt_id")==pid and p.get("pair_id")=="R%02d"%i,"PAIR_ORDER")
        need(p.get("stratum")==expected[pid],"PAIR_STRATUM")
        need({p.get("left_arm"),p.get("right_arm")}=={"H0","H1"},"PAIR_ARMS")
        per[p["stratum"]].append(p["left_arm"])
    need(len(per)==4 and all(collections.Counter(v)=={"H0":3,"H1":3} for v in per.values()),
         "STRATUM_BALANCE")
    need(sum(p["left_arm"]=="H0" for p in pairs)==12,"LEFT_12_12")
    return True

def create_once(public,private_dir):
    entries,by=index_from_public(public)
    d=pathlib.Path(private_dir)
    need(d.is_dir() and not d.is_symlink(),"EXISTING_PRIVATE_DIRECTORY_REQUIRED")
    keyfile=d/KEY_NAME; encrypted=d/ESCROW_NAME
    need(not keyfile.exists() and not encrypted.exists(),"EXISTING_ESCROW_DO_NOT_REKEY")
    sides={}
    rng=secrets.SystemRandom()
    for name,ids in sorted(by.items()):
        chosen=list(ids);rng.shuffle(chosen)
        for pid in ids:sides[pid]="H0" if pid in chosen[:3] else "H1"
    pairs=[]
    for i,e in enumerate(entries,1):
        left=sides[e["id"]]
        pairs.append({"pair_id":"R%02d"%i,"prompt_id":e["id"],"stratum":e["stratum"],
                      "left_arm":left,"right_arm":"H1" if left=="H0" else "H0"})
    validate_pairs(pairs,entries)
    plain=canonical({"schema":"ttm.hdata_s1.owner_private_blind_map.v1","run_id":RUN_ID,"pairs":pairs})
    key=AESGCM.generate_key(bit_length=256); nonce=os.urandom(12)
    ciphertext=AESGCM(key).encrypt(nonce,plain,AAD)
    public_obj={"schema":"ttm.hdata_s1.encrypted_blind_escrow.v1","run_id":RUN_ID,
      "cipher":"AES-256-GCM","aad_b64":base64.b64encode(AAD).decode(),
      "nonce_b64":base64.b64encode(nonce).decode(),
      "ciphertext_b64":base64.b64encode(ciphertext).decode(),
      "plaintext_mapping_sha256":sha(plain),"commitment_sha256":COMMITMENT_SHA,
      "pairs":24,"balanced":"12_12_LEFT;3_3_EACH_OF_FOUR_STRATA",
      "before_model_forward":True,"no_final_plaintext":True}
    public_bytes=canonical(public_obj)+b"\n"
    key_obj={"schema":"ttm.hdata_s1.owner_private_aes_key.v1","run_id":RUN_ID,
      "key_b64":base64.b64encode(key).decode(),
      "public_escrow_sha256":sha(public_bytes),"mapping_sha256":sha(plain),
      "owner_only":True,"NEVER_PUSH_TO_GITHUB":True}
    put_new(keyfile,canonical(key_obj)+b"\n")
    put_new(encrypted,public_bytes)
    return verify(public,private_dir)

def verify(public,private_dir):
    entries,_=index_from_public(public)
    d=pathlib.Path(private_dir);keyfile=d/KEY_NAME;encrypted=d/ESCROW_NAME
    need(all(x.is_file() and not x.is_symlink() for x in [keyfile,encrypted]),"ESCROW_FILES_MISSING")
    kb=keyfile.read_bytes();eb=encrypted.read_bytes()
    k=json.loads(kb);e=json.loads(eb)
    need(e["run_id"]==k["run_id"]==RUN_ID and e["commitment_sha256"]==COMMITMENT_SHA,"RUN_SCOPE")
    need(k["public_escrow_sha256"]==sha(eb),"ESCROW_SHA")
    need(base64.b64decode(e["aad_b64"])==AAD,"AAD_DRIFT")
    plain=AESGCM(base64.b64decode(k["key_b64"])).decrypt(
         base64.b64decode(e["nonce_b64"]),base64.b64decode(e["ciphertext_b64"]),AAD)
    need(sha(plain)==k["mapping_sha256"]==e["plaintext_mapping_sha256"],"PLAIN_SHA")
    payload=json.loads(plain)
    need(payload["run_id"]==RUN_ID and validate_pairs(payload["pairs"],entries),"DECRYPTED_MAPPING")
    return {"status":"PASS_OWNER_PRIVATE_AES256_GCM_ESCROW",
      "public_escrow_sha256":sha(eb),
      "private_key_sha256_FOR_OWNER_ONLY":sha(kb),
      "mapping_plaintext_sha256":sha(plain),
      "pair_count":24,"per_stratum_balance":"PASS_3_3","no_model_forward":True,
      "no_final_prompt_text_read":True,
      "owner_private_key_never_commit":True}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--commitment",required=True)
    ap.add_argument("--private-dir",required=True)
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--create-once",action="store_true")
    g.add_argument("--verify-only",action="store_true")
    a=ap.parse_args()
    report=create_once(a.commitment,a.private_dir) if a.create_once else verify(a.commitment,a.private_dir)
    print(json.dumps(report,sort_keys=True))
if __name__=="__main__":main()
