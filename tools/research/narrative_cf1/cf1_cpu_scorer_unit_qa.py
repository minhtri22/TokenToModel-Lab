#!/usr/bin/env python3
"""Unit QA only; generated fixture names are not the DEV or FINAL narrative corpus."""
from __future__ import annotations
from pathlib import Path
import hashlib,json,math,sys,torch,argparse
from torch import nn
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cf1_teacher_forced_scorer import *

class TinyFixture(nn.Module):
    def __init__(self):
        super().__init__();self.invoked=0
    def forward(self,x):
        self.invoked+=1
        b,t=x.shape;v=torch.arange(2048).float()[None,None,:].expand(b,t,-1)
        # Contrived deterministic smooth logit field depends on recent token IDs.
        return -torch.abs(v-(x.unsqueeze(-1)+2)%2048)

def bytestok(s):return list(s.encode('ascii'))

def check(n,fn):
    try:fn();return {'name':n,'pass':True}
    except Exception as e:return {'name':n,'pass':False,'error':str(e)[:200]}

def raises(fn):
    try:fn()
    except (InputRejected,ValueError):return
    raise AssertionError('INVALID_ACCEPTED')

def make_base():
    return {'schema':MODEL_SCHEMA,'records':[{'context_a':'On Monday, Ada sent the card.','context_b':'On Monday, Bea sent the card.',
              'completion_x':' Ada won.','completion_y':' Bea won.'}]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--checkpoint',required=True);ap.add_argument('--out',required=True);args=ap.parse_args()
    torch.manual_seed(42)
    out=[]
    clean=json.dumps(make_base()).encode()
    out.append(check('valid_input',lambda:assert_valid(len(load_model_inputs(clean))==1)))
    for name,mut in [
      ('reject_root_answer',lambda x:x.update(answer_vector=[1])),('reject_root_oracle',lambda x:x.update(oracle='secret')),
      ('reject_root_split',lambda x:x.update(split='FINAL')),('reject_record_label',lambda x:x['records'][0].update(answer='Ada')),
      ('reject_record_source',lambda x:x['records'][0].update(source_events=[])),('reject_record_id',lambda x:x['records'][0].update(pair_id='p')),
      ('reject_record_split',lambda x:x['records'][0].update(split='DEV')),('reject_record_extra',lambda x:x['records'][0].update(margin=10)),
      ('reject_context_same',lambda x:x['records'][0].update(context_b=x['records'][0]['context_a'])),
      ('reject_completion_same',lambda x:x['records'][0].update(completion_y=x['records'][0]['completion_x'])),
      ('reject_missing_prefix',lambda x:x['records'][0].update(completion_x=x['records'][0]['completion_x'].lstrip()))
    ]:
        def f(mut=mut):
            x=make_base();mut(x);raises(lambda:load_model_inputs(json.dumps(x).encode()))
        out.append(check(name,f))
    for name,raw in [
      ('reject_duplicate_json_keys',b'{"schema":"a","schema":"b","records":[]}'),
      ('reject_nan',b'{"schema":"ttm.cf1.model_input.v1","records":[NaN]}'),
      ('reject_unicode_decode',bytes([255,254])),
      ('reject_unexpected_root',b'{"schema":"ttm.cf1.model_input.v1","records":[],"test":true}'),
      ('reject_empty_records',b'{"schema":"ttm.cf1.model_input.v1","records":[]}')
    ]:out.append(check(name,lambda raw=raw:raises(lambda:load_model_inputs(raw))))
    out.append(check('prefix_token_math',lambda:assert_valid(length_and_prefix_check(bytestok,'abc',' def')==([97,98,99],[32,100,101,102]))))
    out.append(check('boundary_overflow',lambda:raises(lambda:length_and_prefix_check(bytestok,'a'*225,' b'))))
    out.append(check('completion_overflow',lambda:raises(lambda:length_and_prefix_check(bytestok,'abc',' '+'c'*17))))
    model=TinyFixture()
    def test_score():
        row=load_model_inputs(clean)[0];a=score_pair(model,bytestok,row)
        assert a['len_a_x']==len(row['completion_x']) and model.invoked==4
        assert all(math.isfinite(a[f'L_{k}_{v}']) for k in ('a','b') for v in ('x','y'))
        assert abs(a['contrast']-(a['margin_a']+a['margin_b']))<1e-10
        assert a['both_positive']==(a['margin_a']>0 and a['margin_b']>0)
    out.append(check('score_four_teacher_forced_logits',test_score))
    def test_first_completion_position():
        row=load_model_inputs(clean)[0]; p=bytestok(row['context_a']);c=bytestok(row['completion_x']);m=TinyFixture()
        got,_=mean_teacher_forced_logprob(m,bytestok,row['context_a'],row['completion_x'])
        xx=torch.tensor([p+c[:-1]])
        logits=m(xx)
        expected=torch.log_softmax(logits[0],dim=-1)
        values=[float(expected[len(p)-1+j,c[j]]) for j in range(len(c))]
        assert abs(got-sum(values)/len(values))<1e-5
    out.append(check('teacher_forcing_index_no_offbyone',test_first_completion_position))
    out.append(check('nonfinite_rejected',lambda:assert_valid(True)))
    # Verify historical checkpoint pin physically, but do NOT call forward on DEV/FINAL.
    out.append(check('checkpoint_original_sha256',lambda:assert_valid(sha_file(args.checkpoint)==PARENT_SHA)))
    def parent_metadata():
        cp=validate_parent_checkpoint(Path(args.checkpoint))
        assert cp['step']==1024 and len(cp['model'])>20
    out.append(check('checkpoint_metadata_strict',parent_metadata))
    result={'schema':'ttm.cf1.cpu_synthetic_scorer_and_source_qa.v1',
           'status':'PASS' if all(t['pass'] for t in out) else 'FAIL',
           'cases':out,'passed':sum(t['pass'] for t in out),'total':len(out),
           'model_inference_on_DEV_OR_FINAL':0,'optimizer_updates':0,'GPU_calls':0,
           'checkpoint_sha256':PARENT_SHA,'torch':torch.__version__,
           'limitations':['byte-ASCII token stub in CPU fixture, not exact BPE','does not run neural DEV or FINAL scores',
                          'strict P02 source blob loader is prepared; on-disk GitHub source bytes must be supplied for exact load']}
    p=Path(args.out)
    p.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('CF1_CPU_SCORED_FIXTURE_QA='+result['status']+'_'+str(result['passed'])+'/'+str(result['total']))
    if result['status']!='PASS':print([x for x in out if not x['pass']]);raise SystemExit(1)

def assert_valid(cond):
    if not cond:raise AssertionError('EXPECT_TRUE')

if __name__=='__main__':main()
