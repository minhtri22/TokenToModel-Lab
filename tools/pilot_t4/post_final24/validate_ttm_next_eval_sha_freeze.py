#!/usr/bin/env python3
"""Offline, read-only, stdlib validation of TTM post-FINAL24 prompt commitment."""
import argparse, hashlib, json, collections
from pathlib import Path

def sha(b): return hashlib.sha256(b).hexdigest()

def validate(owner_path, public_sha_path, dev_path):
    owner_bytes=Path(owner_path).read_bytes()
    owner=json.loads(owner_bytes)
    public=json.loads(Path(public_sha_path).read_bytes())
    devbytes=Path(dev_path).read_bytes()
    dev=json.loads(devbytes)
    assert sha(owner_bytes)==public['owner_private_eval_file_sha256']
    assert sha(devbytes)==public['dev12_public_sha256']
    assert len(owner['prompts'])==36 and len(dev['prompts'])==12
    final=[x for x in owner['prompts'] if x['cohort']=='BLIND_FINAL']
    assert len(final)==24
    assert [x['id'] for x in final]==[f'NF{i:02}' for i in range(1,25)]
    assert [x['id'] for x in owner['prompts'] if x['cohort']=='DEV']==[f'ND{i:02}' for i in range(1,13)]
    assert len({x['prompt'] for x in owner['prompts']})==36
    assert collections.Counter(x['stratum'] for x in final)=={'object_custody':6,'social_relation':6,'causal_obstacle':6,'temporal_rule':6}
    assert all(x['prompt']==x['prompt'].strip() and x['prompt'][-1] in '.?!' and sha(x['prompt'].encode('utf8'))==x['prompt_utf8_sha256'] for x in owner['prompts'])
    assert [x['prompt_utf8_sha256'] for x in final]==[x['prompt_utf8_sha256'] for x in public['sha256_per_final_prompt']]
    assert all(d['prompt']==o['prompt'] for d,o in zip(dev['prompts'],owner['prompts'][:12]))
    print('NEW_EVAL_OWNER_SHA=PASS')
    print('DEV12_FINAL24=PASS')
    print('FINAL24_PER_PROMPT_SHA=PASS')
    print('SCOPE=STATIC_QA_ONLY_NO_TRAINING_NO_INFERENCE')

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--owner-private',required=True)
    p.add_argument('--public-commit',required=True)
    p.add_argument('--dev',required=True)
    a=p.parse_args();validate(a.owner_private,a.public_commit,a.dev)
