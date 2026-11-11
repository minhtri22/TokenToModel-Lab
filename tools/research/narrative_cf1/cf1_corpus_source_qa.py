#!/usr/bin/env python3
"""Author-side scope QA. For sensitive FINAL use only in owner-private working env.

Never writes final plaintext to public receipt; counts and hashes only.
Review quality remains internal, and semantic labels are not independently human-certified.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import difflib,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
DEV=json.loads((ROOT/'public/CF1_DEV_PUBLIC_ORACLE.json').read_text())['pairs']
FINAL=json.loads((ROOT/'private/CF1_FINAL_PRIVATE_PLAINTEXT_DO_NOT_GITHUB.json').read_text())['pairs']
CAND_NAME=re.compile(r'\b(Mira|Lena|Anna|Jack|Ella|Emma|Nora|Owen|Ada|Bea|Tara|Theo)\b')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def near(a,b):
    def ngrams(s):
        words=re.findall(r'[a-z]+',s.lower());return set(tuple(words[i:i+5]) for i in range(len(words)-4))
    x,y=ngrams(a),ngrams(b)
    return len(x&y)/len(x|y) if x|y else 0

def audit(rows,label):
    ids=Counter(r['pair_id'] for r in rows);motifs=Counter(r['motif_id'] for r in rows)
    families=Counter(r['family'] for r in rows)
    valid=0;shallow=0;shared_last=0;matched_swaps=0
    for r in rows:
        assert r['gold_a']=='x' and r['gold_b']=='y'
        assert r['family'] in ('C1','C2','C3') and len(r['context_a'])<1200
        assert r['context_a']!=r['context_b'] and r['completion_x']!=r['completion_y']
        assert r['completion_x'].startswith(' ') and r['completion_y'].startswith(' ')
        a=CAND_NAME.findall(r['completion_x']);b=CAND_NAME.findall(r['completion_y'])
        assert len(a)==len(b)==1 and a[0]!=b[0]
        ax=CAND_NAME.findall(r['context_a']);by=CAND_NAME.findall(r['context_b'])
        shallow+=int(bool(ax and by and ax[0]==a[0] and by[0]==b[0]))
        swap=r['context_a'].replace(a[0],'__LEFT__').replace(b[0],a[0]).replace('__LEFT__',b[0])
        matched_swaps+=int(swap==r['context_b'])
        last_a=r['context_a'].split('. ')[-1];last_b=r['context_b'].split('. ')[-1]
        shared_last+=int(last_a==last_b)
        valid+=1
    return {'pairs':len(rows),'family_counts':dict(families),'motif_count':len(motifs),
            'motif_repetitions':sorted(set(motifs.values())), 'pair_ids_unique':len(ids)==len(rows),
            'strict_label_orientation_valid':valid,'simple_first_name_heuristic_correct':shallow,
            'simple_first_name_heuristic_total':len(rows),'person_swap_only_context_pairs':matched_swaps,
            'last_sentence_identical_contexts':shared_last}

def main():
    d=audit(DEV,'DEV');f=audit(FINAL,'FINAL')
    dev_motifs=set(x['motif_id'] for x in DEV);final_motifs=set(x['motif_id'] for x in FINAL)
    overlap=dev_motifs&final_motifs
    contexts_dev=[x[k] for x in DEV for k in ('context_a','context_b')]
    contexts_fin=[x[k] for x in FINAL for k in ('context_a','context_b')]
    exact_dup=set(contexts_dev)&set(contexts_fin)
    near_pairs=0;max_near=0.0
    for a in contexts_dev:
        for b in contexts_fin:
            n=near(a,b);max_near=max(max_near,n)
            if n>=0.85:near_pairs+=1
    env=json.loads((ROOT/'public/CF1_FINAL_ENCRYPTED_ENVELOPE.json').read_text())
    import base64
    cipher=base64.b64decode(''.join(env['ciphertext_b64_chunks']),validate=True)
    source_cipher=base64.b64decode(''.join(env['private_author_source_encrypted']['ciphertext_b64_chunks']),validate=True)
    assert env['plaintext_sha256_commitment']==sha(ROOT/'private/CF1_FINAL_PRIVATE_PLAINTEXT_DO_NOT_GITHUB.json')
    assert env['ciphertext_sha256']==hashlib.sha256(cipher).hexdigest()
    assert env['private_author_source_encrypted']['ciphertext_sha256']==hashlib.sha256(source_cipher).hexdigest()
    assert not overlap and not exact_dup
    assert d['pairs']==36 and f['pairs']==72
    result={'schema':'ttm.cf1.narrative_public_DEV_and_private_FINAL.author_content_QA.v1',
        'status':'PASS_FORMAL_SOURCE_QA_WITH_SHALLOW_SHORTCUT_AND_REVIEW_LIMIT',
        'DEV':d,'FINAL_PRIVATE_AGGREGATES_ONLY':f,
        'DEV_FINAL_exact_pair_overlap':len(set(x['pair_id'] for x in DEV)&set(x['pair_id'] for x in FINAL)),
        'DEV_FINAL_motif_id_overlap':len(overlap), 'DEV_FINAL_exact_context_overlap':len(exact_dup),
        'DEV_FINAL_5gram_Jaccard_ge_0_85_pairs':near_pairs,'DEV_FINAL_max_5gram_Jaccard':round(max_near,4),
        'DEV_sha256':sha(ROOT/'public/CF1_DEV_PUBLIC_ORACLE.json'),
        'model_input_sha256':sha(ROOT/'public/CF1_DEV_MODEL_INPUT_ONLY.json'),
        'encrypted_final_ciphertext_sha256':env['ciphertext_sha256'],
        'encrypted_final_author_source_sha256':env['private_author_source_encrypted']['ciphertext_sha256'],
        'final_plaintext_sha256_commitment':env['plaintext_sha256_commitment'],
        'failure_classification':'SHALLOW_FIRST_PERSON_MENTION_PREDICTS_100_PERCENT_IN_SOURCE_GRAMMAR',
        'scientific_state_reasoning_discrimination':'FAIL_SCOPED',
        'data_blindness':'FINAL_LABELS_ENCRYPTED_ONLY_GITHUB',
        'independent_semantic_review':'NOT_EXECUTED',
        'dev_natural_language_draft_is_templated':True,
        'model_inference_executed':False,'training_executed':False,'GPU_used':False,
        'notes':['DEV and FINAL use 36 hand-authored scenario bases, three cast variations each; not 108 structurally independent plots',
                 'Distinct motif IDs do not prove query-conditioned causal-graph OOD',
                 'The first-person-name shortcut works on both A and B; cannot claim state-specific benchmark discrimination',
                 'Do not use private FINAL as science holdout until human/Codex reviewer checks unambiguous labels and structural independence.']}
    p=ROOT/'public/CF1_CORPUS_AUTHOR_SOURCE_QA.json';p.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('CF1_AUTHOR_DATA_SOURCE_QA='+result['status'])
    print(json.dumps({k:result[k] for k in ('DEV','FINAL_PRIVATE_AGGREGATES_ONLY','DEV_FINAL_motif_id_overlap','DEV_FINAL_exact_context_overlap','DEV_FINAL_5gram_Jaccard_ge_0_85_pairs')},sort_keys=True))

if __name__=='__main__':main()
