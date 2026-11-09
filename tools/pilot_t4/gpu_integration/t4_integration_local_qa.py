"""Zero-science integrated CPU regression of frozen T4 trainer on synthetic variable-length windows."""
import sys,json,random,hashlib, tempfile
from pathlib import Path
import numpy as np, torch
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from t4_train_science import (train_one_step, checkpoint_payload,checkpoint_write, checkpoint_load,
                              require_science_lock, sample_exact_step)
from t4_capacity_smoke import p02_module
from t4_eval import fit_baselines, baseline_story_scores, model_story_scores, decide_h1

torch.set_num_threads(2)
SEED=20261108
p02=p02_module(ROOT/'p02_source_exact.py')
cfg=p02.P02Config(vocab_size=2048,max_seq_len=256,n_embd=32,n_layer=1,n_head=4)
npgen=np.random.default_rng(701)
cs=np.array(([256,210,134,178,146,244,101,163,236,206,257] *4)[:43])
cs=np.clip(cs,1,256)
x=np.zeros((len(cs),256),dtype=np.int16);y=np.full((len(cs),256),-100,dtype=np.int16)
for i,c in enumerate(cs):
    ids=npgen.integers(1,2048,size=c+1,dtype=np.int16)
    x[i,:c]=ids[:-1];y[i,:c]=ids[1:]
story=np.arange(len(cs),dtype=np.int32)
data={'train_x':x,'train_y':y,'train_count':cs,'train_story_index':story,
      'val_x':x[:8].copy(),'val_y':y[:8].copy(),'val_count':cs[:8].copy(),'val_story_index':story[:8].copy()}

def new_context():
    random.seed(SEED);np.random.seed(SEED);torch.manual_seed(SEED)
    m=p02.GPT(cfg)
    o=torch.optim.AdamW(m.parameters(),lr=3e-4,betas=(.9,.95),eps=1e-8,weight_decay=.1)
    s=torch.optim.lr_scheduler.LambdaLR(o,lr_lambda=lambda n:1.0)
    g=torch.Generator(device='cpu').manual_seed(SEED+71)
    return m,o,s,g

m,o,s,g=new_context();l1,w1=train_one_step(m,o,s,g,None,data,torch.device('cpu'),'fp32',8)
with tempfile.TemporaryDirectory(prefix='ttm_t4_synth_') as tmp:
    folder=Path(tmp)/'run';folder.mkdir()
    pp=checkpoint_payload(m,o,s,g,None,1,'a'*64,'b'*64,1.23,torch.device('cpu'))
    ready=checkpoint_write(folder,1,pp,[{'step':1,'loss':l1,'windows':w1}],Path(tmp)/'scratch')
    l2,w2=train_one_step(m,o,s,g,None,data,torch.device('cpu'),'fp32',8)
    p_end={k:v.detach().clone() for k,v in m.state_dict().items()}
    o_end=o.state_dict();sampler_end=g.get_state().clone()
    m2,o2,s2,g2=new_context()
    step,spent=checkpoint_load(folder/'checkpoints'/'step_0001',m2,o2,s2,g2,None,torch.device('cpu'),'a'*64,'b'*64)
    l2r,w2r=train_one_step(m2,o2,s2,g2,None,data,torch.device('cpu'),'fp32',8)
    assert step==1 and spent==1.23
    assert (w2,w2r)==(w2,w2)
    assert l2==l2r,(l2,l2r)
    assert all(torch.equal(p_end[k],v) for k,v in m2.state_dict().items())
    assert torch.equal(sampler_end,g2.get_state())
    assert o.state_dict()['param_groups']==o2.state_dict()['param_groups']
    for key in o_end['state']:
        for k,v in o_end['state'][key].items():
            other=o2.state_dict()['state'][key][k]
            assert torch.equal(v,other) if isinstance(v,torch.Tensor) else v==other
    loguni,logbi=fit_baselines(data['train_x'],data['train_y'])
    tcounts,unis,bis=baseline_story_scores(data,loguni,logbi)
    model_sums=model_story_scores(m2,data,torch.device('cpu'),eval_batch=4)
    h1=decide_h1(model_sums,bis,tcounts,boot=1000)
    assert h1['scored_val_targets']==int(cs[:8].sum())
    try:
        require_science_lock(None,None,{'npz_sha256':'b'*64},'c'*64,'d'*64)
    except RuntimeError as e:
        assert 'SCIENCE_NOT_AUTHORIZED' in str(e)
    else:raise AssertionError('lock wrongly granted')
    receipt={'schema':'ttm.t4.synthetic.cpu.trainer.integration.v1','status':'PASS_CPU_SYNTHETIC_DYNAMIC_WINDOW_CHECKPOINT_EVAL',
             'science_executed':False,'tiny_stories_used':False,'gpu_used':False,
             'microbatch_windows':8,'targets_per_step':4096,'synthetic_windows_shape':list(x.shape),
             'synthetic_window_mean_targets':float(cs.mean()),'windows_step1':w1,'windows_step2':w2,
             'step2_loss_exact':l2==l2r,'model_exact':True,'optimizer_exact':True,'sampler_exact':True,
             'checkpoint_sha256':ready['sha256'],'ready_last':True,
             'val_scored_targets':h1['scored_val_targets'],'bigram_model_h1_smoke_only':True,
             'science_lock_denial':True,'source_p02_sha256':hashlib.sha256((ROOT/'p02_source_exact.py').read_bytes()).hexdigest()}
    out=ROOT/'T4_LOCAL_SYNTHETIC_TRAINER_INTEGRATION_QA.json'
    assert not out.exists()
    out.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps(receipt,indent=2));print('RECEIPT_SHA256='+hashlib.sha256(out.read_bytes()).hexdigest())
