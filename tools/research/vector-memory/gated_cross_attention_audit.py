#!/usr/bin/env python3
"""Independent aggregate-level QA for a scoped, non-confirmatory Vector Memory pilot."""
import argparse, ast, hashlib, json
from pathlib import Path

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--runner',required=True,type=Path)
    ap.add_argument('--result',required=True,type=Path)
    ap.add_argument('--replay',required=True,type=Path)
    ap.add_argument('--out',required=True,type=Path)
    a=ap.parse_args()
    code=a.runner.read_text(encoding='utf-8')
    ast.parse(code)
    d=json.loads(a.result.read_text(encoding='utf-8'))
    other=json.loads(a.replay.read_text(encoding='utf-8'))
    h=d['holdout_train_not_used_for_adapter_or_bank']
    v=d['val_previously_examined_exploratory_only']
    hi=h['arms'];vi=v['arms']
    integ=d['integrity']
    checks={
        'experiment_name':d['experiment']=='TTM_VECTOR_MEMORY_GATED_CROSS_ATTENTION_ARCHITECTURE_MINI_TEST',
        'scoped_no':d['status']=='NO_SCOPED_EXPLORATORY',
        'result_bytes_exact_replay':sha(a.result)==sha(a.replay),
        'json_exact_replay':d==other,
        'checkpoint_sha_pinned':d['model']['checkpoint_sha256']=='ee723407b2c25a18be20e26387a3dd8e4a18e2942d469279b6f0748ff86af0dc',
        'pack_sha_pinned':d['model']['train_val_pack_sha256']=='184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913',
        'p02_blob_pinned':d['model']['source_git_blob']=='9762343e06cf800b50574c2871ae1ed58537fb18',
        '64_steps_each':d['design']['steps']==64,
        'bank_fit_holdout_sizes':(d['design']['train_bank_stories'],d['design']['train_fit_stories'],d['design']['train_holdout_stories'])==(512,512,256),
        'previous_val_flagged':d['design']['val_story_count_already_seen_in_prior_diagnostics']==256,
        'checkpoint_not_changed':integ['checkpoint_unchanged'],
        'backbone_frozen':integ['all_original_parameters_frozen'],
        'bank_fit_holdout_no_overlap':integ['bank_fit_holdout_disjoint'],
        'test_not_used':integ['test_never_loaded'],
        'init_residual_exact_bypass':integ['init_zero_delta_exact'],
        'exact_full_table_lookup':integ['original_exact_external_embedding_and_head_bit_exact_on_both_sets'],
        'no_raw_rows_in_export':integ['private_rows_not_exported'],
        'holdout_ab_exact':hi['A_base']['nll']==hi['B_exact']['nll'],
        'val_ab_exact':vi['A_base']['nll']==vi['B_exact']['nll'],
        'holdout_bypass_exact':hi['A_base']['nll']==hi['E_bypass']['nll'],
        'val_bypass_exact':vi['A_base']['nll']==vi['E_bypass']['nll'],
        'C_better_than_old_but_worse_than_base':hi['OLD_adapter']['nll']>hi['C_cross_attention']['nll']>hi['A_base']['nll'],
        'shuffled_beats_C_holdout':hi['D_shuffled_values']['nll']<hi['C_cross_attention']['nll'],
        'shuffled_beats_C_VAL':vi['D_shuffled_values']['nll']<vi['C_cross_attention']['nll'],
        'cross_training_completed':d['training']['cross_last16']<d['training']['cross_start16'],
        'old_training_completed':d['training']['old_last16']<d['training']['old_start16'],
        'historical_old_adapter_reproduced':d['historical_adapter_regression_on_prior_128_val']['reproduced'] and abs(d['historical_adapter_regression_on_prior_128_val']['old_adapter_nll']-3.7390940189361572)<2e-5,
        'holdout_criterion_not_met':not h['verdict_yes'],
        'previous_val_criterion_not_met':not v['verdict_yes'],
        'new_cross_has_gate_range':0 <=h['additional']['gate_min']<=h['additional']['mean_gate']<=h['additional']['gate_max']<=1,
        'holdout_bootstrap_not_positive':h['additional']['gain_bootstrap95_descriptive'][1]<0,
        'val_bootstrap_not_positive':v['additional']['gain_bootstrap95_descriptive'][1]<0,
    }
    report={'verdict':'PASS' if all(checks.values()) else 'FAIL', 'passed':sum(checks.values()),'total':len(checks),'checks':checks,
            'sha256':{'runner':sha(a.runner),'result':sha(a.result),'replay':sha(a.replay)},
            'scope':'independent aggregate assertions + byte-identical deterministic CPU replay; not independent unseen science data'}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'verdict':report['verdict'],'passed':report['passed'],'total':report['total']},ensure_ascii=False))
    if report['verdict']!='PASS':
        print({k:v for k,v in checks.items() if not v})
        raise SystemExit(1)
if __name__=='__main__':main()
