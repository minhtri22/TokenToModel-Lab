#!/usr/bin/env python3
"""Owner-machine-only FINAL BPE audit: decrypt in RAM and disclose aggregated lengths.

Never print, write, or commit private text, answer keys or AES key.
This QA does not open FINAL for model scoring.
"""
from __future__ import annotations
import argparse,base64,hashlib,json,sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from cf1_exact_t1_bpe import PinnedT1BPE
def length_and_prefix_check(encode,context,completion):
    p=list(encode(context));whole=list(encode(context+completion))
    if whole[:len(p)]!=p:raise ValueError('PREFIX_TOKENIZATION_CHANGED')
    suffix=whole[len(p):]
    if not 1<=len(p)<=224 or not 1<=len(suffix)<=16 or len(whole)>256:
        raise ValueError('FINAL_BPE_LENGTH_CAP_EXCEEDED')
    return p,suffix

def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    a=argparse.ArgumentParser()
    a.add_argument('--envelope',required=True);a.add_argument('--private-key',required=True)
    a.add_argument('--t1-manifest',required=True);a.add_argument('--receipt',required=True)
    args=a.parse_args()
    out=Path(args.receipt)
    if out.exists():raise FileExistsError('REFUSE_OVERWRITE')
    env=json.loads(Path(args.envelope).read_text('utf8'));keyfile=json.loads(Path(args.private_key).read_text('utf8'))
    key=base64.b64decode(keyfile['aes256_key_b64'],validate=True)
    ct=base64.b64decode(''.join(env['ciphertext_b64_chunks']),validate=True)
    if sha(ct)!=env['ciphertext_sha256']:raise ValueError('CIPHERTEXT_SHA_BAD')
    raw=AESGCM(key).decrypt(base64.b64decode(env['nonce_b64']),ct,env['aad'].encode())
    if sha(raw)!=env['plaintext_sha256_commitment'] or sha(raw)!=keyfile['final_plaintext_sha256']:
        raise ValueError('PRIVATE_FINAL_SOURCE_HASH_DIFF')
    corpus=json.loads(raw.decode('utf8'))
    pairs=corpus['pairs']
    if corpus['schema']!='ttm.cf1.owner_private_final.v1' or len(pairs)!=72:
        raise ValueError('FINAL_SCHEMA_COUNT')
    tok=PinnedT1BPE(args.t1_manifest)
    prefix_lengths=[];answer_lengths=[];equal=0;no_truncation=0
    for r in pairs:
        lens=[]
        for context in (r['context_a'],r['context_b']):
            for ending in (r['completion_x'],r['completion_y']):
                prefix,part=length_and_prefix_check(tok.encode,context,ending)
                prefix_lengths.append(len(prefix));answer_lengths.append(len(part));lens.append(len(part))
                no_truncation+=1
        equal+=int(lens[0]==lens[1] and lens[2]==lens[3])
    result={'schema':'ttm.cf1.owner_private_final_exact_T1_BPE_readonly_QA.v1',
            'status':'PASS' if equal==72 else 'HOLD_UNEQUAL_COMPLETION_TOKENS',
            'final_pairs':72,'total_teacher_forced_checks':no_truncation,
            'min_context_tokens':min(prefix_lengths),'max_context_tokens':max(prefix_lengths),
            'min_answer_tokens':min(answer_lengths),'max_answer_tokens':max(answer_lengths),
            'same_length_candidate_pairs':equal,
            'checkpoint_inference_calls':0,'optimizer_updates':0,'GPU_calls':0,
            'model_labels_or_private_text_emitted':False,
            'source_plaintext_sha256_commitment':sha(raw),
            'T1_merges_sha256':tok.manifest_sha256,
            'not_a_science_unlock':True}
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf8') as f:json.dump(result,f,sort_keys=True,indent=2);f.write('\n')
    print(result['status']+'; NO_FINAL_PLAINTEXT_EXPORTED')
if __name__=='__main__':main()
