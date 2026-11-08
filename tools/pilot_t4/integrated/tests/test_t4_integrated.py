import sys, pathlib, json, hashlib
import numpy as np
import pytest
import torch

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from t4_data_pack import windows_for_ids
from t4_train_science import sample_exact_step,require_science_lock,_numpy_rng_to_primitives
from t4_eval import fit_baselines,baseline_story_scores,decide_h1,load_private_pack,model_story_scores
from t4_capacity_smoke import p02_module,candidate_decision


def mock_data():
    windows=[]
    for i in range(4):
        ids=list(range(270+i))
        ids=[x%2048 for x in ids]
        windows+=windows_for_ids(ids)
    x=np.stack([t[0] for t in windows]);y=np.stack([t[1] for t in windows])
    c=np.array([t[2] for t in windows],dtype=np.int16)
    story_idx=np.repeat(np.arange(4,dtype=np.int32),[len(windows_for_ids([x%2048 for x in range(270+i)])) for i in range(4)])
    return {'train_x':x,'train_y':y,'train_count':c,'train_story_index':story_idx,
            'val_x':x,'val_y':y,'val_count':c,'val_story_index':story_idx}


def test_windows_no_cross_story_count():
    a=windows_for_ids(list(range(103)))
    assert len(a)==1 and sum(x[2] for x in a)==102
    assert np.all(a[0][1][102:]==-100)
    b=windows_for_ids(list(range(600)))
    assert [x[2] for x in b]==[256,256,87]
    assert sum(x[2] for x in b)==599
    assert b[0][1][-1]==256 and b[1][0][0]==256


def test_exact4096_sampler_and_only_valid_labels():
    data=mock_data()
    groups,n=sample_exact_step(data,torch.Generator(device='cpu').manual_seed(11),2)
    assert n>=16
    assert sum(int(np.sum(y!=-100)) for x,y in groups)==4096
    assert all(x.shape==y.shape and x.shape[1]==256 and x.shape[0]<=2 for x,y in groups)


def test_baselines_train_only_and_story_bootstrap():
    d=mock_data();loguni,logbi=fit_baselines(d['train_x'],d['train_y'])
    assert logbi.shape==(2048,2048)
    assert np.allclose(np.exp(logbi).sum(axis=1),1.0)
    counts,unis,bis=baseline_story_scores(d,loguni,logbi)
    assert sum(counts)==int(d['val_count'].sum())
    good=decide_h1(bis*.85,bis,counts)
    assert good['h1_pass'] and good['relative_nll_improvement']>=.05 and good['bootstrap_95pct_gain_ci'][0]>0
    bad=decide_h1(bis*1.01,bis,counts)
    assert not bad['h1_pass']


def test_private_pack_no_test_and_sha(tmp_path):
    d=mock_data();p=tmp_path/'private.npz';np.savez_compressed(p,**d)
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    m={'schema':'ttm.t4.private.train_val.windowpack.v1','contains_test':False,
       'contains_reversible_train_val_tokens':True,'npz_sha256':digest,
       'counts':{'train_next_token_targets_unique':int(d['train_count'].sum()),
         'val_next_token_targets':int(d['val_count'].sum()),'train_stories':4,'val_stories':4}}
    mp=tmp_path/'manifest.json';mp.write_text(json.dumps(m))
    dd,_=load_private_pack(p,mp);assert sorted(dd.files)==sorted(d)
    m['contains_test']=True;mp.write_text(json.dumps(m))
    with pytest.raises(RuntimeError,match='TEST_VIOLATION'):load_private_pack(p,mp)


def test_science_fails_closed(tmp_path):
    pack={'npz_sha256':'a'*64}
    with pytest.raises(RuntimeError,match='SCIENCE_NOT_AUTHORIZED'):
        require_science_lock(None,None,pack,'c'*64,'d'*64)
    p=tmp_path/'lock.json';p.write_text('{}')
    with pytest.raises(RuntimeError,match='SCIENCE_AUTHORIZATION_NOT_GRANTED'):
        require_science_lock(p,hashlib.sha256(p.read_bytes()).hexdigest(),pack,'c'*64,'d'*64)


def test_ranking_capacity_provisional_only():
    r=[{'precision':'fp16','microbatch_windows':2,'worst_seconds':2.0,'peak_cuda_reserved_bytes':2*(1024**3)},
       {'precision':'fp32','microbatch_windows':2,'worst_seconds':6.0,'peak_cuda_reserved_bytes':3*(1024**3)}]
    c=candidate_decision(r,16*(1024**3))
    assert c['precision']=='fp16'
    assert r[0]['feasible_on_measured_smoke'] and not r[1]['feasible_on_measured_smoke']


def test_exact_p02_source_pinned():
    p=p02_module(ROOT/'p02_source_exact.py')
    model=p.GPT(p.P02Config(max_seq_len=256,n_embd=256,n_layer=4,n_head=4))
    assert sum(p.numel() for p in model.parameters())==3749376


def test_cpu_model_val_story_evaluator():
    d=mock_data()
    p=p02_module(ROOT/'p02_source_exact.py')
    model=p.GPT(p.P02Config(max_seq_len=256,n_embd=32,n_layer=1,n_head=4))
    scores=model_story_scores(model,d,'cpu',eval_batch=3)
    assert len(scores)==4 and np.all(np.isfinite(scores)) and np.all(scores>0)


def test_rng_primitives_for_weights_only(tmp_path):
    np.random.seed(42)
    a=_numpy_rng_to_primitives()
    f=tmp_path/'rng.pt'
    torch.save({'rng':a},f)
    restored=torch.load(f,map_location='cpu',weights_only=True)['rng']
    np.random.set_state((restored[0],np.asarray(restored[1],dtype=np.uint32),restored[2],restored[3],restored[4]))
    assert np.isfinite(np.random.random())


def test_capacity_notebook_no_science_and_source_pinned():
    import ast
    n=json.loads((ROOT/'TTM_T4_Synthetic_Capacity_20261108_v1.ipynb').read_text())
    assert len(n['cells'])==5
    for c in n['cells']:
        if c['cell_type']=='code':ast.parse(''.join(c['source']))
    source='\n'.join(''.join(c['source']) for c in n['cells'])
    assert 't4_capacity_smoke.py' in source and 'SCIENCE_LOCK=HOLD' in source

def test_ready_last_checkpoint_roundtrip_cpu_synthetic(tmp_path):
    from t4_train_science import checkpoint_payload,checkpoint_write,checkpoint_load
    p=p02_module(ROOT/'p02_source_exact.py')
    cfg=p.P02Config(vocab_size=2048,max_seq_len=256,n_embd=32,n_layer=1,n_head=4)
    model=p.GPT(cfg);opt=torch.optim.AdamW(model.parameters(),lr=.0003)
    sch=torch.optim.lr_scheduler.LambdaLR(opt,lr_lambda=lambda step:1.)
    sampler=torch.Generator(device='cpu').manual_seed(42)
    before=[t.detach().clone() for t in model.parameters()]
    payload=checkpoint_payload(model,opt,sch,sampler,None,256,'a'*64,'b'*64,12.0,torch.device('cpu'))
    folder=tmp_path/'run';folder.mkdir()
    ready=checkpoint_write(folder,256,payload,[{'step':256}],tmp_path/'scratch')
    assert ready['step']==256
    ckpt=folder/'checkpoints'/'step_0256'
    assert (ckpt/'READY.json').exists()
    for t in model.parameters():t.data.add_(.5)
    # On CPU no CUDA RNG device state to restore.
    step,spent=checkpoint_load(ckpt,model,opt,sch,sampler,None,torch.device('cpu'),'a'*64,'b'*64)
    assert step==256 and spent==12
    assert all(torch.equal(before_t,now_t) for before_t,now_t in zip(before,model.parameters()))
    with pytest.raises(FileExistsError):checkpoint_write(folder,256,payload,[],tmp_path/'scratch')

def test_capacity_real_window_inflation_can_block_90min():
    from t4_capacity_accept import assess
    cap={'schema':'ttm.t4.capacity.synthetic.v1','science_executed':False,'status':'PASS_PROVISIONAL_CAPACITY_ONLY',
         'records':[{'precision':'fp16','microbatch_windows':2,'gradient_accumulation':8,
           'worst_seconds':2.5,'projected_science_seconds_with_25pct_reserved':3413.3,'memory_reserved_ratio':.15}]}
    pack={'schema':'ttm.t4.private.train_val.windowpack.v1','contains_test':False,
          'counts':{'train_next_token_targets_unique':700_000,
                    'train_reuse_factor_for_4194304_target_budget':4194304/700_000,
                    'train_mean_valid_targets_per_window':100}}
    r=assess(cap,pack)
    assert r['status']=='CAPACITY_HOLD' and r['selected'] is None
    pack['counts']['train_mean_valid_targets_per_window']=256
    r2=assess(cap,pack)
    assert r2['status'].startswith('CAPACITY_PASS')


def test_science_notebook_fails_closed_before_drive():
    import ast
    nb=json.loads((ROOT/'TTM_T4_Science_FailClosed_20261108_v1.ipynb').read_text())
    for c in nb['cells']:
        if c['cell_type']=='code':ast.parse(''.join(c['source']))
    cell2=''.join(nb['cells'][2]['source'])
    assert "EXPECTED_LOCK_SHA256='NOT_ISSUED'" in cell2
    assert 'drive.mount' in cell2 and cell2.index('T4_SCIENCE_LOCK_NOT_ISSUED_STOP') < cell2.index('drive.mount')
