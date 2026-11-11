#!/usr/bin/env python3
"""Independent aggregate-only audit of the TTM Vector Memory diagnostic receipt."""
import argparse, hashlib, json, math
from pathlib import Path

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def chk(test,name,tests):
    tests[name]=bool(test)
    if not test:raise AssertionError(name)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--result',required=True,type=Path)
    p.add_argument('--script',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    a=p.parse_args()
    o=json.loads(a.result.read_text(encoding='utf-8'))
    tests={}
    chk(o['experiment']=='TTM_VECTOR_MEMORY_RETRIEVAL_SIGNAL_DIAGNOSTIC','experiment',tests)
    chk(o['verdict']=='PAUSE_VECTOR_MEMORY_RESEARCH_NO_RELIABLE_INCREMENTAL_SIGNAL','verdict',tests)
    chk(o['integrity']['checkpoint_unchanged'] and o['integrity']['no_gradients'],'frozen_no_grad',tests)
    chk(o['integrity']['no_test'] and o['integrity']['no_private_text_or_token_rows_in_output'],'no_test_or_private_export',tests)
    chk(o['integrity']['train_bank_fit_disjoint'] and o['integrity']['VAL_disjoint_from_TRAIN'],'story_disjointness',tests)
    chk(o['pins']['checkpoint_sha256']=='ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc','checkpoint_pin',tests)
    chk(o['pins']['train_val_pack_sha256']=='184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913','pack_pin',tests)
    chk(o['design']['bank_selection_sha256']=='4b8546f6d9c22df481d4b9be6a9e0d97691179bde21cb48d38e44e580eb60922','bank_selection_pin',tests)
    chk(o['design']['val_previous_selection_sha256']=='fb9d072fbb817cc8cc5a90367f2175d7b789d29a2140a660fbf2803332fa584f','previous_val_pin',tests)
    h=o['metrics']['hidden_context'];l=o['metrics']['last_token_embedding']
    chk(all(h[k]['targets']==(256 if k=='all_val256' else 128) for k in h),'val_counts',tests)
    chk(math.isclose(h['previous_val128']['top1_hit'],.1484375,abs_tol=1e-9),'prior_top1_reproduction',tests)
    chk(abs(h['previous_val128']['base_frozen_nll']-3.637324333190918)<2e-6,'prior_baseline_reproduction',tests)
    chk(h['additional_val128']['top1_hit']>h['additional_val128']['top1_random_shuffle_mean'],'label_association_better_than_shuffle',tests)
    chk(h['additional_val128']['top1_permutation_one_sided_p']<=.05,'label_permutation_signal',tests)
    chk(h['additional_val128']['top1_hit']>l['additional_val128']['top1_hit'],'hidden_better_than_last_token',tests)
    chk(h['additional_val128']['base_minus_knn_fusion0.10_mean']<0,'no_gain_on_additional_val',tests)
    chk(h['additional_val128']['base_minus_knn_fusion0.10_bootstrap95pct_CI'][1]<0,'paired_bootstrap_no_gain',tests)
    chk(h['additional_val128']['nll_with_knn_fusion']['lambda_0.05']>h['additional_val128']['base_frozen_nll'],'lambda05_no_gain',tests)
    chk(h['additional_val128']['nll_with_knn_fusion']['lambda_0.25']>h['additional_val128']['base_frozen_nll'],'lambda25_no_gain',tests)
    chk(h['additional_val128']['knn_fusion0.10_minus_shuffled_mean']<0,'retrieval_better_than_shuffled_fusion',tests)
    chk(o['design']['new_val_disjoint_from_previous'],'additional_val_disjoint',tests)
    raw=a.result.read_text(encoding='utf-8')
    chk(not any(x in raw for x in ['train_x','train_y','val_x','val_y','raw_story_text']), 'no_raw_array_keys', tests)
    receipt={'status':'PASS','test_count':len(tests),'tests':tests,
             'script_sha256':digest(a.script),'result_sha256':digest(a.result),
             'replay_required':'BYTE_EXACT_REPLAY_VERIFIED_SEPARATELY',
             'limitations':'Checks aggregate report structure and internal consistency; not a new independent reimplementation of the retrieval algorithm.'}
    a.out.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('AUDIT_PASS',len(tests),'/',len(tests))
if __name__=='__main__':main()
