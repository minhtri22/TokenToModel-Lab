#!/usr/bin/env python3
"""FC01 V2: versioned source-only amendment. No GPU, training, inference or TEST access.

Read exactly seven LF-pinned V1 sources; create a new V2 source directory;
preserve V1 private corpus; call only existing integrated PS source QA with
--mode audit. Unknown hashes: fail before writing any source file.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(r"D:\WORK\RESEARCH\TokenToModel-Lab")
OLD = ROOT / "_tmp" / "fc01_onepacket_20261113"
NEW = ROOT / "_tmp" / "fc01_onepacket_20261113_v2"
V1 = "7214213c79002943cbb9f7d0c6c25a81ba7f522c7218dcd4297a2c8465084bd6"
V2 = "becc0408880aaed8bd5eb6fdf3997e62d5131c187a48331a03ae37d41aaa1aa3"
SOURCE_SHA_V1 = {
 "fc01_build_private_corpus.py": "1fc0000bfe507fdceebc0a595fc703b5c66fdb74a70f07dcc4e23a745e6a3b90",
 "fc01_integrated_static_qa.py": "d3fec73129766a2ff1f95bc3690de41a85cb6621ff3b0abe0a945e86359284b0",
 "fc01_independent_contract_tests.py": "419c3beca59193de2b29c8e26a9cfc9ba0583346f4da160c72ee17fc6b291d3f",
 "fc01_train_eval_once.py": "b80c7fe84c22f3474520019a1649396f01d4dba9a757c5a9651279797c4434e7",
 "fc01_pinned_bpe.py": "d90ddbcdbea8450d7605cf7e65936efd032344b8d7793c2272d4d0870cfbff01",
 "Invoke-TTM-FC01-Integrated-Readiness-PS51.ps1": "714bbe2490d20eb6faddbfdaf983c352c09b886fd2259e76b23041bb4b7f864f",
 "README_FC01_ONEPACKET_VI.md": "f0aa8bf7e31f627802aa8469ad67bd197c208c98991a82c840119f13d90b6231",
}
SOURCE_SHA_V2 = {
 "fc01_build_private_corpus.py": "a9978a1961a2d062e5229ad91593eddb01f7fcfab00c4dfb55cc3df316053c98",
 "fc01_integrated_static_qa.py": "f4f205ed4be0021faf99b3e73f4c0fb80ef4d1ce095ee5985507ca3f1e33cc3e",
 "fc01_independent_contract_tests.py": "316b6d8a26881abbcc333aedbf14ef0342f65731b56690f8a09dbd24e34f8f6e",
 "fc01_train_eval_once.py": "b786a4468ba104786df7683da9b1cf19d2334d9cc203dd19c3e7d6f10e2e93be",
 "fc01_pinned_bpe.py": SOURCE_SHA_V1["fc01_pinned_bpe.py"],
 "Invoke-TTM-FC01-Integrated-Readiness-PS51.ps1": "cf8ad6aa83d83319201bb90e7d89cfa1adda18bb2e6dea8d5f6e88cc38c4678b",
 "README_FC01_ONEPACKET_VI.md": SOURCE_SHA_V1["README_FC01_ONEPACKET_VI.md"],
}
assert set(SOURCE_SHA_V1) == set(SOURCE_SHA_V2)

def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def replace_one(s: str, a: str, b: str) -> str:
    found = s.count(a)
    if found != 1:
        raise RuntimeError("FC01_V2_AMENDMENT_ANCHOR_COUNT_MISMATCH_" + str(found) + ":" + a[:75])
    return s.replace(a,b)

def amend(name: str, source: str) -> str:
    x = source
    if name == "fc01_build_private_corpus.py":
        replacements = (
            ("SCHEMA='ttm.fc01.original_counterfactual_corpus.v1'",
             "SCHEMA='ttm.fc01.original_counterfactual_corpus.v2_bpe_amended'"),
            ("'a':' The keeper checked the upper bin.',",
             "'a':' The keeper used the upstairs bin.',"),
            ("'b':' The keeper checked the lower bin.',",
             "'b':' The keeper used the downstairs bin.',"),
            ("'facts':('upper','lower')},",
             "'facts':('upstairs','downstairs')},"),
            ("the keeper had one goal: place a ceramic token at the {fact} counter.",
             "the keeper had one goal: place a ceramic token on the {fact} table."),
            ("The task was to place a ceramic token at the {fact} counter.",
             "The task was to place a ceramic token on the {fact} table."),
            ("'a':' The keeper carried it to the north counter.',",
             "'a':' The keeper put it on the north table.',"),
            ("'b':' The keeper carried it to the south counter.',",
             "'b':' The keeper put it on the south table.',"),
            ("pick='A' if int(f['family_id'].rsplit('-',1)[-1])%2==0 else 'B'",
             "pick='A' if ((int(f['family_id'].rsplit('-',1)[-1])//8 + int(f['family_id'].rsplit('-',1)[-1])%8)%2==0) else 'B'"),
            ("'source':'fc01_assistant_authored_template_original_20261113',",
             "'source':'fc01_assistant_authored_template_original_20261113_v2_bpe_amended',"),
            ("'schema':'ttm.fc01.original_counterfactual_safe_receipt.v1',",
             "'schema':'ttm.fc01.original_counterfactual_safe_receipt.v2_bpe_amended',"),
        )
        for a,b in replacements: x = replace_one(x,a,b)
    elif name == "fc01_integrated_static_qa.py":
        x = replace_one(x, "'ttm.fc01.original_counterfactual_corpus.v1'",
                        "'ttm.fc01.original_counterfactual_corpus.v2_bpe_amended'")
        marker = " assert arms['B_CF_MLE']==arms['C_CF_CONTRAST']\n"
        addition = """ # D0 label must not reveal ITEM or ADJECTIVE by construction (each 4 A and 4 B).
 for cat in CATEGORIES:
  a0=[e for e in arms['A_BASE_MLE'] if e['category']==cat and e['paraphrase']==0]
  for item in ITEMS:
   rows=[e['condition'] for e in a0 if next(f for f in fs if f['family_id']==e['family_id'])['site_descriptor'].split(' ',1)[1]==item]
   assert collections.Counter(rows)=={'A':4,'B':4},('D0_ITEM_LABEL_LEAKAGE',cat,item,rows)
  for adj in ADJECTIVES[:8]:
   rows=[e['condition'] for e in a0 if next(f for f in fs if f['family_id']==e['family_id'])['site_descriptor'].split(' ',1)[0]==adj]
   assert collections.Counter(rows)=={'A':4,'B':4},('D0_ADJECTIVE_LABEL_LEAKAGE',cat,adj,rows)
"""
        x = replace_one(x, marker, marker+addition)
    elif name == "fc01_independent_contract_tests.py":
        marker = " tests['T15_FROZEN_ARMS_AND_SEEDS']='PASS'\n"
        addition = """ # V2 negative control: reconstruct former item-parity singleton labeling.
 q=copy.deepcopy(obj)
 by_id={f['family_id']:f for f in q['families']}
 for ep in q['arms']['A_BASE_MLE']:
  i=int(ep['family_id'].rsplit('-',1)[-1]);state='A' if i%2==0 else 'B'
  f=by_id[ep['family_id']];ep['condition']=state
  ep['prompt']=f['context'][f'{state}_{ep["paraphrase"]}']
  ep['answer_correct']=f['y'+state]
  ep['answer_wrong']=f['y'+('B' if state=='A' else 'A')]
  ep['text']=ep['prompt']+ep['answer_correct']
 try:check(q)
 except AssertionError as e:
  assert 'D0_ITEM_LABEL_LEAKAGE' in str(e), ('WRONG_ANTI_LEAKAGE_FAILURE',str(e))
 else:raise AssertionError('ITEM_PARITY_LABEL_LEAKAGE_NOT_CAUGHT')
 tests['T16_DETECT_D0_ITEM_LABEL_LEAKAGE']='PASS'
"""
        x = replace_one(x, marker, marker+addition)
    elif name == "fc01_train_eval_once.py":
        x = replace_one(x,V1,V2)
    elif name == "Invoke-TTM-FC01-Integrated-Readiness-PS51.ps1":
        for a,b in (
            (r"_tmp\fc01_onepacket_20261113'",r"_tmp\fc01_onepacket_20261113_v2'"),
            (r"_tmp\TTM_FC01_OWNER_CORPUS_20261113'",r"_tmp\TTM_FC01_OWNER_CORPUS_20261113_v2'"),
            (r"_tmp\TTM_FC01_SOURCE_BUNDLE_20261113'",r"_tmp\TTM_FC01_SOURCE_BUNDLE_20261113_v2'"),
        ):
            x=replace_one(x,a,b)
        if x.count(V1)!=2:
            raise RuntimeError("FC01_V2_PS_EXPECT_TWO_CORPUS_SHA_OCCURRENCES")
        x=x.replace(V1,V2)
        if "--mode audit --inputs-dir $Input" not in x or "--mode train" in x:
            raise RuntimeError("FC01_V2_PS_NOT_SOURCE_ONLY")
    return x

def main() -> int:
    if sys.version_info[:2] != (3,12):
        raise RuntimeError("FC01_REQUIRES_PINNED_PYTHON_312")
    if not (ROOT / ".git").exists() or not OLD.is_dir():
        raise RuntimeError("FC01_WRONG_PROJECT_OR_MISSING_V1_SOURCES")
    if ROOT.resolve() not in NEW.resolve().parents:
        raise RuntimeError("FC01_SOURCE_PATH_ESCAPE")
    prepared = {}
    for name,original_sha in SOURCE_SHA_V1.items():
        raw=(OLD/name).read_bytes()
        if digest(raw)!=original_sha:
            raise RuntimeError("FC01_V1_SOURCE_SHA_MISMATCH_NO_WRITE:"+name+":"+digest(raw))
        output=amend(name, raw.decode("utf-8")).encode("utf-8")
        if digest(output)!=SOURCE_SHA_V2[name]:
            raise RuntimeError("FC01_V2_SOURCE_SHA_MISMATCH_NO_WRITE:"+name+":"+digest(output))
        prepared[name]=output
    print("FC01_V1_PINNED_SOURCE_7_OF_7=PASS")
    print("FC01_V2_TRANSFORMED_SOURCE_7_OF_7=PASS_PREWRITE")
    if NEW.exists():
        if not NEW.is_dir():
            raise RuntimeError("FC01_V2_OUTPUT_IS_NOT_A_DIRECTORY")
        for name,expected in SOURCE_SHA_V2.items():
            file=NEW/name
            if not file.is_file() or digest(file.read_bytes())!=expected:
                raise RuntimeError("FC01_V2_PARTIAL_OR_MODIFIED_SOURCE_NO_OVERWRITE:"+name)
        print("FC01_V2_EXISTING_SOURCE=REUSE_EXACT_SHA")
    else:
        NEW.mkdir(parents=False,exist_ok=False)
        for name,data in prepared.items():
            with (NEW/name).open("xb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
        for name,expected in SOURCE_SHA_V2.items():
            if digest((NEW/name).read_bytes())!=expected:
                raise RuntimeError("FC01_V2_POSTWRITE_SOURCE_SHA_MISMATCH:"+name)
        print("FC01_V2_SOURCE_CREATED_WITH_UTF8_LF=PASS_7_OF_7")
    # Only source/rights/static QA and the runner --mode audit are invoked below.
    cmd=["powershell.exe","-NoProfile","-ExecutionPolicy","Bypass",
         "-File",str(NEW/"Invoke-TTM-FC01-Integrated-Readiness-PS51.ps1")]
    print("FC01_V2_CALL_INTEGRATED_SOURCE_ONLY_QA_NO_GPU")
    completed=subprocess.run(cmd, cwd=str(ROOT),check=False)
    if completed.returncode!=0:
        print("FC01_V2_OWNER_SOURCE_QA=HOLD_EXIT_"+str(completed.returncode))
        return 2
    print("FC01_V2_OWNER_SOURCE_QA=PASS_SCOPED_NOT_SCIENCE_GO")
    print("FC01_SCIENCE=HOLD_PREEXEC TRAINING=NO GPU=NO D1=SEALED")
    return 0

if __name__=="__main__":
    try:sys.exit(main())
    except Exception as e:
        print("FC01_V2_PREEXEC=HOLD_"+type(e).__name__+":"+str(e),file=sys.stderr)
        sys.exit(2)
