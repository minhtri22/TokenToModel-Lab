#!/usr/bin/env python3
"""G1 v1b cross-model ridge science: signed gate and frozen TEST one-shot.

Numpy only. Consumes *private numeric feature packs* (produced separately after
science authorization); never downloads Qwen or opens TinyStories. Synthetic QA
requires no files. No scientific run without explicit permit and distinct review.
"""
from __future__ import annotations
import argparse, hashlib, io, json, os, sys
import g1_science_guard_v1b as guard
from pathlib import Path
import numpy as np

MANIFEST_SHA = '6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6'
T1_SHA = '9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9'
ALPHAS = (1., 10., 100.)
SHUFFLE_N, CKA_N, BOOT_N = 1000, 1000, 2000
SEED_SHUFFLE, SEED_CKA, SEED_BOOT = 20261110, 20261110, 20261111
COUNTS = {'TRAIN': 128, 'DEV': 64, 'TEST': 64}
EPS = 1e-6


def require(ok, message):
    if not ok:
        raise RuntimeError('STOP_G1_' + message)


def sha_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as fd:
        for b in iter(lambda: fd.read(8 << 20), b''):
            h.update(b)
    return h.hexdigest()


def jbytes(obj):
    return (json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def standardize(train, other):
    mu = train.mean(axis=0)
    sd = np.maximum(train.std(axis=0, ddof=0), EPS)
    return (train-mu)/sd, (other-mu)/sd, mu, sd


def gram_fit(x):
    k = x @ x.T
    eig, u = np.linalg.eigh((k+k.T)*0.5)
    return eig, u


def dual_predict(eig, u, xtrain, xnew, ycenter, alpha):
    require(alpha in ALPHAS, 'ALPHA_NOT_FROZEN')
    co = u @ ((u.T @ ycenter) / (np.maximum(eig, 0.)[:, None] + alpha))
    return (xnew @ xtrain.T) @ co


def macro_r2(pred, truth, train_mean, allow_degenerate=False):
    sst = ((truth - train_mean)**2).sum(axis=0)
    if not allow_degenerate:
        require(bool(np.all(sst >= 1e-8)), 'TEST_SST_DEGENERATE')
    else:
        require(bool(np.all(sst >= 1e-8)), 'DEV_SST_DEGENERATE')
    return float(np.mean(1. - ((pred-truth)**2).sum(axis=0) / sst))


def choose_alpha(candidates):
    # Candidate tuples (alpha, DEV macro-R2); tie -> larger alpha.
    require(len(candidates) == len(ALPHAS), 'ALPHA_GRID_INCOMPLETE')
    require(all(np.isfinite(score) for _,score in candidates), 'NONFINITE_DEV_SCORE')
    return float(max(candidates, key=lambda x: (x[1], x[0]))[0])


def verify_arrays(pack, expected_n, source_dim=1024, target_dim=2048):
    require(set(pack) == {'ids','s','t','r'}, 'PACK_UNEXPECTED_FIELDS')
    require(pack['s'].shape == (expected_n,source_dim), 'SOURCE_SHAPE')
    require(pack['t'].shape == (expected_n,target_dim), 'TARGET_SHAPE')
    require(pack['r'].shape == (expected_n,8), 'RESPONSES_SHAPE')
    for name in ('s','t','r'):
        require(pack[name].dtype.kind == 'f', 'PACK_DTYPE_'+name)
        require(bool(np.isfinite(pack[name]).all()), 'PACK_NONFINITE_'+name)
    ids = [str(v) for v in pack['ids'].tolist()]
    require(len(ids)==expected_n and len(set(ids))==expected_n, 'PACK_ID_DUPLICATE')
    require(all(len(i)==64 and all(c in '0123456789abcdef' for c in i) for i in ids), 'PACK_ID_FORMAT')
    return ids


def load_pack(path, split, manifest, source_dim=1024, target_dim=2048, *, run_id, root, trusted_pack_sha):
    p=guard.ensure_regular_no_redirect(path,root)
    receipt_path=p.with_suffix('.receipt.json')
    guard.ensure_regular_no_redirect(receipt_path,root)
    raw=p.read_bytes()
    guard.require(guard.sha_bytes(raw)==trusted_pack_sha,'TRUSTED_PACK_SHA_MISMATCH')
    receipt=json.loads(receipt_path.read_text('utf-8'))
    return guard.parse_authenticated_pack(raw,receipt,split=split,manifest=manifest,
            run_id=run_id,source_dim=source_dim,target_dim=target_dim)


def manifest_check(path):
    require(sha_file(path)==MANIFEST_SHA, 'MANIFEST_SHA')
    m = json.loads(Path(path).read_text(encoding='utf-8'))
    require(m['t1_split_manifest_sha256']==T1_SHA, 'T1_LINEAGE')
    require(m['counts']==COUNTS, 'MANIFEST_COUNTS')
    all_rows = [x for split in COUNTS for x in m['splits'][split]]
    require(len(all_rows)==256, 'MANIFEST_TOTAL')
    ids=[x['source_story_sha256'] for x in all_rows]
    pref=[x['normalized_prefix_utf8_sha256'] for x in all_rows]
    require(len(set(ids))==256 and len(set(pref))==256, 'MANIFEST_LEAKAGE')
    return m


def permit_check(envelope, *, phase, workspace, run_id):
    # NO user-selected pin: unprovisioned authority key => mandatory HOLD.
    data=Path(__file__).read_bytes()
    actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\x00'+data).hexdigest()
    expected={'reviewed_core_blob':actual, 'workspace':str(workspace),
              'run_id':run_id,'phase':phase}
    return guard.verify_signed_permit(envelope,expected)


def prepare(train,dev, shuffle_n=SHUFFLE_N):
    ns,nt=train['s'].shape[1],train['t'].shape[1]
    verify_arrays(train,128,ns,nt)
    verify_arrays(dev,64,ns,nt)
    require(not(set(train['ids'].tolist())&set(dev['ids'].tolist())), 'TRAIN_DEV_OVERLAP')
    require(bool(np.all(train['r'].std(axis=0,ddof=0)>=1e-5)), 'TRAIN_FUNCTION_STD_DEGENERATE')
    s,sd,_,_=standardize(train['s'].astype('float64'),dev['s'].astype('float64'))
    t,td,_,_=standardize(train['t'].astype('float64'),dev['t'].astype('float64'))
    r0 = train['r'].astype('float64').mean(axis=0)
    y = train['r'].astype('float64')-r0
    truth=dev['r'].astype('float64')
    require(bool(np.all(((truth-r0)**2).sum(axis=0)>=1e-8)), 'DEV_SST_DEGENERATE')
    se,su=gram_fit(s)
    te,tu=gram_fit(t)
    p_choices=[]
    for a in ALPHAS:
        pr=dual_predict(te,tu,t,td,y,a)+r0
        p_choices.append((a,macro_r2(pr,truth,r0,allow_degenerate=True)))
    p_alpha=choose_alpha(p_choices)
    # P target-hidden -> functional response; reduce aligned model fit to 8D.
    pcoef=tu @ ((tu.T @ y)/(np.maximum(te,0.)[:,None]+p_alpha))
    p_weights=t.T @ pcoef
    reduced_t = t @ p_weights
    a_choices=[]; b_choices=[]
    for a in ALPHAS:
        pa=dual_predict(se,su,s,sd,reduced_t,a)+r0
        pb=dual_predict(se,su,s,sd,y,a)+r0
        a_choices.append((a,macro_r2(pa,truth,r0,True)))
        b_choices.append((a,macro_r2(pb,truth,r0,True)))
    aligned_alpha=choose_alpha(a_choices)
    direct_alpha=choose_alpha(b_choices)
    rng=np.random.default_rng(SEED_SHUFFLE)
    null_alphas=[]; permutation_digest=hashlib.sha256()
    for _ in range(shuffle_n):
        perm=rng.permutation(len(s))
        permutation_digest.update(perm.astype('<i4').tobytes())
        perm_reduced=reduced_t[perm]
        choices=[(a,macro_r2(dual_predict(se,su,s,sd,perm_reduced,a)+r0,
                             truth,r0,True)) for a in ALPHAS]
        null_alphas.append(choose_alpha(choices))
    return {'schema':'ttm.six.g1.fit_dev_frozen_v1',
       'aligned_alpha':aligned_alpha,'direct_alpha':direct_alpha,
       'target_probe_alpha':p_alpha,
       'null_alphas':null_alphas,
       'null_permutation_sha256':permutation_digest.hexdigest(),
       'null_count':shuffle_n,
       'seed_shuffle':SEED_SHUFFLE,
       'seed_cka':SEED_CKA,'seed_boot':SEED_BOOT,
       'primary_layer':28,'function_count':8,'test_touched':False,
       'control_oracle_dev_macro_r2':float(max(x[1] for x in p_choices)),
       'direct_dev_macro_r2':float(max(x[1] for x in b_choices)),
       'aligned_dev_macro_r2':float(max(x[1] for x in a_choices))}


def cka(a,b):
    a=a-a.mean(axis=0); b=b-b.mean(axis=0)
    gram_a=a@a.T; gram_b=b@b.T
    numer=float(np.sum(gram_a*gram_b))
    denom=float(np.sqrt(np.sum(gram_a**2)*np.sum(gram_b**2)))
    require(denom>0., 'CKA_ZERO_VARIANCE')
    return numer/denom


def evaluate(train, dev, test, frozen, *, permutation_n=SHUFFLE_N,
             cka_n=CKA_N, bootstrap_n=BOOT_N):
    ns,nt=train['s'].shape[1],train['t'].shape[1]
    for name,pack,n in (('TRAIN',train,128),('DEV',dev,64),('TEST',test,64)):
        verify_arrays(pack,n,ns,nt)
    idsets=[set(pack['ids'].tolist()) for pack in (train,dev,test)]
    require(not (idsets[0]&idsets[1] or idsets[0]&idsets[2] or idsets[1]&idsets[2]), 'SPLIT_ID_LEAKAGE')
    require(frozen['null_count']==permutation_n and len(frozen['null_alphas'])==permutation_n, 'NULL_COUNT_PIN')
    require(frozen['primary_layer']==28 and frozen['function_count']==8, 'FROZEN_FUNCTIONS')
    require(bool(np.all(train['r'].std(axis=0,ddof=0)>=1e-5)), 'TRAIN_FUNCTION_STD_DEGENERATE')
    s,sx,_,_=standardize(train['s'].astype('float64'),test['s'].astype('float64'))
    t,tx,_,_=standardize(train['t'].astype('float64'),test['t'].astype('float64'))
    rmean=train['r'].astype('float64').mean(axis=0)
    y=train['r'].astype('float64')-rmean
    truth=test['r'].astype('float64')
    if not bool(np.all(((truth-rmean)**2).sum(axis=0)>=1e-8)):
        return {'schema':'ttm.six.g1.science_result_v1b',
                'verdict':'INCONCLUSIVE_DEGENERATE_TEST',
                'test_one_shot_consumed':True,'science_scope':'64_TEST_FEASIBILITY'}
    se,su=gram_fit(s);te,tu=gram_fit(t)
    pa=float(frozen['target_probe_alpha'])
    pcoef=tu@((tu.T@y)/(np.maximum(te,0.)[:,None]+pa))
    pw=t.T@pcoef
    reduced_t=t@pw
    pred_a=dual_predict(se,su,s,sx,reduced_t,float(frozen['aligned_alpha']))+rmean
    pred_b=dual_predict(se,su,s,sx,y,float(frozen['direct_alpha']))+rmean
    pred_o=dual_predict(te,tu,t,tx,y,pa)+rmean
    r2a=macro_r2(pred_a,truth,rmean)
    r2b=macro_r2(pred_b,truth,rmean)
    r2o=macro_r2(pred_o,truth,rmean)
    rng=np.random.default_rng(SEED_SHUFFLE)
    null=[];pdigest=hashlib.sha256()
    for alpha in frozen['null_alphas']:
        perm=rng.permutation(len(s))
        pdigest.update(perm.astype('<i4').tobytes())
        result=dual_predict(se,su,s,sx,reduced_t[perm],float(alpha))+rmean
        null.append(macro_r2(result,truth,rmean))
    require(pdigest.hexdigest()==frozen['null_permutation_sha256'], 'PERMUTATION_CHANGED')
    p_perm=(1+sum(x>=r2a for x in null))/(1+permutation_n)
    p95=float(np.quantile(np.array(null),0.95))
    ck=guard.safe_cka(test['s'].astype('float64'),test['t'].astype('float64'))
    if ck['status']!='PASS_CKA':
        return {'schema':'ttm.six.g1.science_result_v1b',
                'verdict':'INCONCLUSIVE_GEOMETRY_DEGENERATE',
                'test_one_shot_consumed':True,'science_scope':'64_TEST_FEASIBILITY'}
    cobs=ck['cka']
    ck_rng=np.random.default_rng(SEED_CKA)
    cv=[]
    for _ in range(cka_n):
        pv=ck_rng.permutation(len(test['s']))
        cv.append(cka(test['s'].astype('float64')[pv],test['t'].astype('float64')))
    cka_p=(1+sum(x>=cobs for x in cv))/(1+cka_n)
    boot=guard.stable_bootstrap_delta(pred_a,truth,rmean,n=bootstrap_n,seed=SEED_BOOT)
    require(boot['status']=='PASS_STATISTICS_VALID','BOOT_TERMINAL_INCONCLUSIVE')
    lower=boot['bootstrap_lower']
    oracle_ok=r2o>=0.2
    functional=(r2a>=0.1 and r2a-p95>=0.1 and p_perm<=0.01 and lower>0.)
    geometry=(cka_p<=0.01)
    verdict=('PASS_SCOPED_FEASIBILITY_NOT_CAUSAL_SIX' if oracle_ok and functional and geometry
             else 'INCONCLUSIVE_CONTROL_UNQUALIFIED' if not oracle_ok
             else 'INCONCLUSIVE_SCOPED_FEASIBILITY_NOT_PASS')
    # Projection/retrieval diagnostic, not required for primary verdict.
    acoef=su@((su.T@t)/(np.maximum(se,0.)[:,None]+frozen['aligned_alpha']))
    aligned=sx@s.T@acoef
    cos=(aligned@tx.T)/(np.maximum(np.linalg.norm(aligned,axis=1,keepdims=True),EPS)*
                        np.maximum(np.linalg.norm(tx,axis=1,keepdims=True).T,EPS))
    retrieval=float(np.mean(np.argmax(cos,axis=1)==np.arange(64)))
    return {'schema':'ttm.six.g1.science_result_v1b','verdict':verdict,
        'science_sample_size':{'TRAIN':128,'DEV':64,'TEST':64},
        'aligned_macro_r2':r2a,'direct_macro_r2':r2b,'oracle_macro_r2':r2o,
        'mean_baseline_macro_r2':0.,'shuffle_p95_macro_r2':p95,
        'gain_vs_shuffle_p95':r2a-p95,'permutation_p':float(p_perm),
        'bootstrap_95_lower_aligned_minus_mean':lower,
        'bootstrap_estimand':boot['bootstrap_estimand'],
        'cka':cobs,'cka_permutation_p':float(cka_p),
        'retrieval_at_1_diagnostic':retrieval,'null_count':permutation_n,
        'bootstrap_count':bootstrap_n,'cka_null_count':cka_n,
        'science_scope':'64_TEST_FEASIBILITY_ONLY_NO_SIX_SPECIFIC_MECHANISM',
        'qwen_finetuned':False, 'theory':'A_then_P_is_linear_in_source_hidden'}


def synthetic_qa():
    rng=np.random.default_rng(20261109)
    dim_s,dim_t=12,24
    w=rng.normal(size=(dim_s,dim_t))/4
    q=rng.normal(size=(dim_t,8))/4
    def fixture(label,n):
        s=rng.normal(size=(n,dim_s)).astype('float64')
        t=(s@w+0.2*rng.normal(size=(n,dim_t))).astype('float64')
        r=(t@q+0.05*rng.normal(size=(n,8))).astype('float64')
        return {'ids':np.array([hashlib.sha256(f'{label}-{i}'.encode()).hexdigest() for i in range(n)]),
                's':s,'t':t,'r':r}
    train,dev,test=fixture('train',128),fixture('dev',64),fixture('test',64)
    frozen=prepare(train,dev,shuffle_n=13)
    require(frozen['null_count']==13 and not frozen['test_touched'], 'SYNTHETIC_PREP')
    result=evaluate(train,dev,test,frozen,permutation_n=13,cka_n=17,bootstrap_n=31)
    require(np.isfinite(result['aligned_macro_r2']), 'SYNTHETIC_FINITE')
    require(result['null_count']==13 and result['bootstrap_count']==31, 'SYNTHETIC_COUNTS')
    dup={k:v.copy() for k,v in test.items()};dup['ids'][0]=train['ids'][0]
    try:
        evaluate(train,dev,dup,frozen,permutation_n=13,cka_n=17,bootstrap_n=31)
    except RuntimeError as exc:
        require('SPLIT_ID_LEAKAGE' in str(exc), 'SYNTHETIC_NEGATIVE_WRONG')
    else:
        raise RuntimeError('STOP_G1_SYNTHETIC_NEGATIVE_LEAK_NOT_DETECTED')
    return {'status':'PASS_SYNTHETIC_ONLY_NO_SCIENCE','tests':6,
            'no_test_files_read':True,'no_weights_or_raw_text_read':True,
            'negative_overlap_caught':True,'one_shot_not_consumed':True}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',required=True,choices=['synthetic-qa','prepare','finalize'])
    ap.add_argument('--work',type=Path); ap.add_argument('--permit',type=Path)
    ap.add_argument('--run-id')
    args=ap.parse_args()
    if args.mode=='synthetic-qa':
        print(json.dumps(synthetic_qa(),sort_keys=True));return
    require(args.work and args.permit and args.run_id,'ARGS_REQUIRED')
    work=args.work.resolve(strict=True)
    # Versioned G1 v1b source is never allowed to expand the project scope.
    if os.name=='nt':
        root=Path(r'D:\WORK\RESEARCH\TokenToModel-Lab').resolve(strict=True)
        require(work.is_relative_to(root) and work.name=='ttm_six_g1_science_private','WORK_SCOPE_WINDOWS')
    elif sys.platform.startswith('linux'):
        require(work==Path('/content/ttm_six_g1_science_private'),'WORK_SCOPE_COLAB')
    else: require(False,'UNSUPPORTED_HOST')
    envelope=json.loads(args.permit.read_text(encoding='utf-8'))
    admission=permit_check(envelope,phase=args.mode,workspace=work,run_id=args.run_id)
    manifest=manifest_check(work/'G1_PREFIX_IDS_128_64_64_PRIVATE_METADATA.json')
    # A trusted stage receipt binds the accepted pack hashes to the signed run.
    ledger=admission.get('pack_sha_by_split')
    require(isinstance(ledger,dict) and 'TRAIN' in ledger and 'DEV' in ledger,
            'PACK_DIGESTS_NOT_IN_SIGNED_ADMISSION')
    train_path=work/'G1_FEATURES_TRAIN.npz'; dev_path=work/'G1_FEATURES_DEV.npz'
    train=load_pack(train_path,'TRAIN',manifest,run_id=args.run_id,root=work,
                    trusted_pack_sha=ledger['TRAIN'])
    dev=load_pack(dev_path,'DEV',manifest,run_id=args.run_id,root=work,
                  trusted_pack_sha=ledger['DEV'])
    freeze_path=work/'G1_FIT_DEV_FROZEN.json'
    if args.mode=='prepare':
        require(not freeze_path.exists(),'FIT_ALREADY_FROZEN')
        frozen=prepare(train,dev)
        frozen.update({'schema':'ttm.six.g1.fit_dev_frozen_v1b',
                       'train_pack_sha256':ledger['TRAIN'],
                       'dev_pack_sha256':ledger['DEV'],
                       'manifest_sha256':MANIFEST_SHA,
                       'run_id':args.run_id})
        with freeze_path.open('xb') as f:
            f.write(jbytes(frozen));f.flush();os.fsync(f.fileno())
        print(json.dumps({'status':'PASS_FIT_DEV_ONLY_TEST_UNOPENED',
                          'fit_sha256':sha_file(freeze_path),'test_touched':False}))
        return
    # Validate the FULL freeze and the exact DEV/SHUFFLE replay before opening TEST.
    require('fit_sha256' in admission,'FIT_HASH_MISSING_IN_SIGNED_ADMISSION')
    frozen_bytes=guard.ensure_regular_no_redirect(freeze_path,work).read_bytes()
    frozen=guard.validate_frozen_dev(frozen_bytes,admission['fit_sha256'],
                                    ledger['TRAIN'],ledger['DEV'],run_id=args.run_id)
    replay=prepare(train,dev)
    require(all(replay[k]==v for k,v in frozen.items() if k in replay),
            'FIT_DEV_SELECTION_CHANGED')
    require('TEST' in ledger,'TEST_PACK_SHA_MISSING')
    # Consume TEST before reading TEST bytes (even a hash); preserve on failure.
    marker=work/'G1_TEST_READ_ONE_SHOT_CONSUMED.marker'
    with marker.open('x',encoding='utf-8') as f:
        f.write('CONSUMED_BEFORE_TEST_READ\n');f.flush();os.fsync(f.fileno())
    test_path=work/'G1_FEATURES_TEST.npz'
    test=load_pack(test_path,'TEST',manifest,run_id=args.run_id,root=work,
                   trusted_pack_sha=ledger['TEST'])
    report=evaluate(train,dev,test,frozen)
    report.update({'test_pack_sha256':ledger['TEST'],'fit_dev_sha256':admission['fit_sha256'],
                   'manifest_sha256':MANIFEST_SHA,'test_one_shot_consumed':True})
    with (work/'G1_SCIENCE_RESULT_PRIVATE.json').open('xb') as f:
        f.write(jbytes(report));f.flush();os.fsync(f.fileno())
    print(json.dumps({'status':'TERMINAL_SCIENCE_ONE_SHOT',
                      'report_sha256':sha_file(work/'G1_SCIENCE_RESULT_PRIVATE.json'),
                      'verdict':report['verdict'],'test_one_shot_consumed':True}))


if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(json.dumps({'status':'STOP_G1_FAIL_CLOSED','error_type':type(exc).__name__,
                          'error':str(exc)[:500],'science_not_claimed':True}),file=sys.stderr)
        raise SystemExit(1)
