#!/usr/bin/env python3
"""Owner-private CF1 FINAL verification; never writes plaintext or key to GitHub.

Public receipt contains only counts, schema, hashes, and boolean outcomes.
Use this only inside the authorized TTM project root with a private key file.
"""
from __future__ import annotations
import argparse,base64,hashlib,json
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def sha(b):return hashlib.sha256(b).hexdigest()
def decode(s):return base64.b64decode(s,validate=True)
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--envelope',required=True);ap.add_argument('--private-key',required=True)
    ap.add_argument('--receipt',required=True)
    a=ap.parse_args()
    dst=Path(a.receipt)
    if dst.exists():raise FileExistsError('REFUSE_RECEIPT_OVERWRITE')
    e=json.loads(Path(a.envelope).read_text('utf8'))
    k=json.loads(Path(a.private_key).read_text('utf8'))
    if e['schema']!='ttm.cf1.final.aes256gcm.public.envelope.v1' or k['schema']!='ttm.cf1.owner_private_final_key.v1':raise RuntimeError('BAD_ESCROW_SCHEMAS')
    key=decode(k['aes256_key_b64']);assert len(key)==32
    ct=decode(''.join(e['ciphertext_b64_chunks']))
    if sha(ct)!=e['ciphertext_sha256'] or sha(ct)!=k['ciphertext_sha256']:raise RuntimeError('CIPHERTEXT_SHA_MISMATCH')
    raw=AESGCM(key).decrypt(decode(e['nonce_b64']),ct,e['aad'].encode('ascii'))
    if sha(raw)!=e['plaintext_sha256_commitment'] or sha(raw)!=k['final_plaintext_sha256']:raise RuntimeError('FINAL_PLAINTEXT_COMMITMENT_MISMATCH')
    obj=json.loads(raw.decode('utf8')); rows=obj['pairs']
    if len(rows)!=72 or obj['schema']!='ttm.cf1.owner_private_final.v1':raise RuntimeError('FINAL_COUNT_OR_SCHEMA')
    counts={f:sum(r['family']==f for r in rows) for f in ('C1','C2','C3')}
    if counts!={'C1':24,'C2':24,'C3':24}:raise RuntimeError('FINAL_FAMILY_BALANCE')
    sc=e['private_author_source_encrypted'];scb=decode(''.join(sc['ciphertext_b64_chunks']))
    if sha(scb)!=sc['ciphertext_sha256'] or sha(scb)!=k['private_author_source_ciphertext_sha256']:raise RuntimeError('SOURCE_CIPHER_SHA_MISMATCH')
    source=AESGCM(key).decrypt(decode(sc['nonce_b64']),scb,sc['aad'].encode('ascii'))
    if sha(source)!=sc['source_plaintext_sha256_commitment'] or sha(source)!=k['private_author_source_plaintext_sha256']:raise RuntimeError('SOURCE_PLAIN_SHA_MISMATCH')
    out={'schema':'ttm.cf1.owner_private_final_readonly_escrow_verification.v1',
         'status':'PASS_AES256GCM_TWO_AUTHENTICATED_DECRYPTIONS_AND_COMMITMENTS',
         'final_pairs':72,'family_counts':counts,
         'final_plaintext_sha256_commitment':sha(raw),
         'private_author_source_sha256_commitment':sha(source),
         'ciphertext_sha256':sha(ct),'author_ciphertext_sha256':sha(scb),
         'owner_key_read':True,'owner_key_not_exported':True,
         'model_inference':False,'final_scores':0,'original_TTM_TEST_Q1Q2_reads':0,
         'warnings':['This verifies cryptographic custody, not semantic correctness or blind structural independence.',
                     'No private FINAL text, key, nonce unblinding action, or source is printed or stored in this receipt.']}
    dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('x',encoding='utf8') as f:json.dump(out,f,indent=2,sort_keys=True);f.write('\n')
    print(out['status']+'; PAIRS=72; KEY/PLAINTEXT_NOT_EMITTED')
if __name__=='__main__':main()
