#!/usr/bin/env python3
"""Small independent, read-only post-run audit; no private data access."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    if len(sys.argv)!=5: raise SystemExit('usage: adapter_qa.py pilot.json replay.json runner.py audit.json')
    primary,replay,runner,out=map(Path,sys.argv[1:])
    r=json.loads(primary.read_text(encoding='utf-8'))
    q=json.loads(replay.read_text(encoding='utf-8'))
    arms=r['arms'];comp=r['comparisons'];integ=r['integrity'];method=r['design']
    checks={
      'replay_bytes_identical':sha(primary)==sha(replay),
      'replay_values_identical':r==q,
      'exact_lookup_same_nll':arms['A_original']['nll_nats']==arms['B_exact']['nll_nats'],
      'exact_lookup_same_accuracy':arms['A_original']['top1_accuracy']==arms['B_exact']['top1_accuracy'],
      'exact_lookup_logits_bit_exact':comp['A_B_bit_exact_logits'] and integ['A_B_bit_exact'],
      'backbone_unchanged':integ['checkpoint_frozen_unchanged'],
      'train_bank_disjoint':integ['train_bank_disjoint'] and method['bank_training_overlap_story_count']==0,
      'val_not_used_in_training':integ['val_targets_excluded_from_training'],
      'test_not_accessed':integ['test_not_accessed'],
      'train_and_memory_different_stories':method['train_adapter']==512 and method['memory_bank']==512,
      'same_adapter_parameters':r['training']['C_memory_adapter']['num_trainable_parameters']==r['training']['E_no_memory_adapter']['num_trainable_parameters'],
      'val_sample_128':all(v['n_val_targets']==128 for v in arms.values()),
      'no_improvement_over_original':arms['C_memory_adapter']['nll_nats']>=arms['A_original']['nll_nats'],
      'no_improvement_over_shuffle':arms['C_memory_adapter']['nll_nats']>=arms['D_shuffled_memory']['nll_nats'],
      'verdict_no':r['verdict']=='NO_SCOPED_EXPLORATORY',
      'private_no_token_sequences':('train_x' not in str(r) and 'val_x' not in str(r)),
    }
    audited={'experiment':'TTM_VECTOR_MEMORY_TRAIN_ONLY_ADAPTER_VS_EXACT_LOOKUP_SMALL_PILOT',
             'audit':'EXPLORATORY_RESULT_REPLAY_AND_CONSISTENCY',
             'checks':checks,'all_checks_pass':all(checks.values()),
             'pilot_result_sha256':sha(primary),'replay_result_sha256':sha(replay),
             'runner_sha256':sha(runner),
             'limitations':'Audit checks exact replay and JSON consistency; not independent science or independent code implementation.'}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(audited,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'audit_status':'PASS' if audited['all_checks_pass'] else 'FAIL','checks':checks,'result_sha256':sha(primary)},indent=2))
    if not audited['all_checks_pass']:raise SystemExit(1)
if __name__=='__main__':main()
