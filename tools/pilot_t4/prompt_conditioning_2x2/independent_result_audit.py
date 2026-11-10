#!/usr/bin/env python3
"""Read-only arithmetic/metadata auditor; does NOT import the source runner.

Only consumes the synthetic JSON output. Does not read dataset/checkpoint/test.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path

ARMS='ABCD'


class AuditError(ValueError): pass


def ck(cond,why):
    if not cond:raise AuditError(why)


def audit(d):
    ck(d.get('schema')=='ttm.small4m.2x2.synthetic_preflight.result.v1','BAD_SCHEMA')
    ck(d.get('status')=='SYNTHETIC_SAMPLER_PASS_NOT_TRAINING','BAD_SYNTHETIC_STATUS')
    ck(d.get('source_dataset')=='SYNTHETIC_INVENTED_ONLY','DATASET_SOURCE_NOT_SYNTHETIC')
    ck(d.get('real_TRAIN_VAL_pack_read') is False,'REAL_PACK_ACCESS_NOT_PROVEN_ABSENT')
    ck(d.get('model_weights_loaded') is False,'CHECKPOINT_MAY_HAVE_BEEN_LOADED')
    ck(d.get('optimizer_updates')==0 and d.get('GPU_training') is False and d.get('science_inference') is False,'SCIENCE_EXECUTION_NOT_ZERO')
    ck(d.get('synthetic_seed')==20261110,'SYNTHETIC_SEED_CHANGED')
    ck(d.get('steps')==128 and d.get('targets_per_step')==4096,'FROZEN_BUDGET_CHANGED')
    ck(d.get('microbatch_windows')==8,'MICROBATCH_CHANGED')
    ck(d.get('synthetic_train_stories')==40 and d.get('synthetic_total_windows')==64,'SYNTHETIC_FIXTURE_DRIFT')
    entries=d.get('per_step')
    ck(isinstance(entries,list) and len(entries)==128,'NOT_128_STEPS')
    totals={a:0 for a in ARMS}; fw={a:0 for a in ARMS};slots={a:0 for a in ARMS}
    chain={a:hashlib.sha256() for a in ARMS}
    for k,item in enumerate(entries):
        ck(item.get('step')==1025+k,'STEP_NUMBER_NOT_CONTIGUOUS')
        for a in ARMS:
            info=item.get(a)
            ck(isinstance(info,dict),'MISSING_ARM_'+a)
            ck(isinstance(info.get('draws'),int) and info['draws']>0,'INVALID_FORWARD_DRAW')
            ck(info.get('targets')==4096,'TARGETS_NOT_MATCHED')
            ck(info.get('slots')==256*info['draws'],'FORWARD_SLOTS_MISMATCH')
            ck(info.get('microbatches')==(info['draws']+7)//8,'MICROBATCH_COUNT_MISMATCH')
            h=info.get('plan_sha256','')
            ck(isinstance(h,str) and len(h)==64 and all(c in '0123456789abcdef' for c in h),'PLAN_SHA_MALFORMED')
            chain[a].update(bytes.fromhex(h))
            totals[a]+=info['targets'];fw[a]+=info['draws'];slots[a]+=info['slots']
        ck(all(item[a]['draws']==item['A']['draws'] for a in ARMS),'FORWARD_COUNT_NOT_SAME_PER_STEP')
        ck(all(item[a]['slots']==item['A']['slots'] for a in ARMS),'FORWARD_SLOTS_NOT_SAME_PER_STEP')
        ck(all(item[a]['microbatches']==item['A']['microbatches'] for a in ARMS),'MICROBATCH_NOT_SAME_PER_STEP')
        ck(item['A']['plan_sha256']==item['C']['plan_sha256'],'A_C_DATA_PLAN_DRIFT')
        ck(item['B']['plan_sha256']==item['D']['plan_sha256'],'B_D_DATA_PLAN_DRIFT')
    ck(d.get('total_valid_label_exposures')==totals,'AGGREGATE_TARGETS_MISMATCH')
    ck(d.get('total_forward_windows')==fw,'AGGREGATE_FORWARD_WINDOWS_MISMATCH')
    ck(d.get('total_forward_token_slots')==slots,'AGGREGATE_FORWARD_SLOTS_MISMATCH')
    ck(set(totals.values())=={128*4096},'VALID_TARGET_EXPOSURES_UNFAIR')
    ck(len(set(fw.values()))==1 and len(set(slots.values()))==1,'FORWARD_COMPUTE_UNFAIR')
    ck(d.get('plan_digest_by_arm')=={a:h.hexdigest() for a,h in chain.items()},'CHAIN_DIGEST_MISMATCH')
    ck(chain['A'].hexdigest()==chain['C'].hexdigest(),'A_C_CHAIN_MISMATCH')
    ck(chain['B'].hexdigest()==chain['D'].hexdigest(),'B_D_CHAIN_MISMATCH')
    cc=d.get('first_story_window_draw_counts')
    ck(isinstance(cc,dict) and cc.get('B')==fw['B'] and cc.get('D')==fw['D'],'NOT_ALL_B_D_FIRST_STORY')
    ck(cc.get('A')==cc.get('C') and cc.get('A')<fw['A'],'ORIGINAL_SAMPLER_FIRST_WINDOW_MALFORMED')
    ck(isinstance(d.get('replacement_count_changed_window_id'),int) and d['replacement_count_changed_window_id']>0,'DATA_SAMPLING_NO_DIFFERENCE')
    ck('NOT ESTABLISHED' in d.get('caveat',''),'REAL_DATA_FEASIBILITY_MISREPRESENTED')
    return {'status':'PASS_INDEPENDENT_AGGREGATE_AUDIT','total_target_exposures':totals,
            'forward_windows':fw,'forward_token_slots':slots,
            'first_story_window_draw_counts':cc,
            'replacement_count_changed_window_id':d['replacement_count_changed_window_id'],
            'checked_steps':len(entries)}


def negative_audit_tests(obj):
    # Each mutation is designed to fail a disjoint contract; some failure
    # detectors may overlap but no altered evidence is accepted as canonical.
    mutants=[]
    def add(field,mutate):
        x=copy.deepcopy(obj);mutate(x);mutants.append((field,x))
    add('schema',lambda x:x.update(schema='tampered'))
    add('source_dataset',lambda x:x.update(source_dataset='PRIVATE_TRAIN'))
    add('real_train_access',lambda x:x.update(real_TRAIN_VAL_pack_read=True))
    add('model_loaded',lambda x:x.update(model_weights_loaded=True))
    add('optimizer_updates',lambda x:x.update(optimizer_updates=1))
    add('steps',lambda x:x.update(steps=129))
    add('lost_step',lambda x:x['per_step'].pop())
    add('step_index',lambda x:x['per_step'][11].update(step=1048))
    add('target_shortfall',lambda x:x['per_step'][3]['B'].update(targets=4095))
    add('forward_count',lambda x:x['per_step'][5]['D'].update(draws=99))
    add('forward_slots',lambda x:x['per_step'][5]['C'].update(slots=1))
    add('microbatch_count',lambda x:x['per_step'][0]['A'].update(microbatches=0))
    add('A_C_schedule',lambda x:x['per_step'][2]['C'].update(plan_sha256='0'*64))
    add('B_D_schedule',lambda x:x['per_step'][0]['D'].update(plan_sha256='1'*64))
    add('head_summary_digest',lambda x:x['plan_digest_by_arm'].update(A='0'*64))
    add('head_target_sum',lambda x:x['total_valid_label_exposures'].update(A=1))
    add('first_count',lambda x:x['first_story_window_draw_counts'].update(B=0))
    add('no_replacement',lambda x:x.update(replacement_count_changed_window_id=0))
    add('bootstrap_claim',lambda x:x.update(caveat='real source was definitely feasible'))
    add('microbatch_size',lambda x:x.update(microbatch_windows=4))
    failed=0; first=[]
    for name,x in mutants:
        try:audit(x)
        except AuditError as e:
            failed+=1
            first.append({'fixture':name,'rejected':str(e)})
        else:
            raise RuntimeError('NEGATIVE_AUDIT_MUTANT_WAS_ACCEPTED:'+name)
    return {'negative_fixtures':len(mutants),'rejected':failed,'detail':first}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    raw=a.input.read_bytes()
    obj=json.loads(raw)
    result=audit(obj)
    result['source_file_sha256']=hashlib.sha256(raw).hexdigest()
    result['negative']=negative_audit_tests(obj)
    result['trust_scope']='SOURCE_JSON_ARITHMETIC_ONLY_NOT_MODEL_OR_REAL_DATA_QA'
    result['source_input']='SYNTHETIC_ONLY'
    result['independent_human_review']=False
    with a.output.open('x',encoding='utf-8') as f:
        json.dump(result,f,sort_keys=True,indent=2)
        f.write('\n')
    print(result['status'], 'NEGATIVE', result['negative']['rejected'],'/',result['negative']['negative_fixtures'])


if __name__=='__main__':main()
