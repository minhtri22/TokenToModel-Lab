"""Independent Windows/CPU fixtures. No private inputs, real permits, or GPU."""
import contextlib
import copy
import hashlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import patch
import zipfile

import numpy as np
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import g1_science_core_v1b as c
import g1_science_guard_v1b as g
import g1_science_private_feature_extractor_v1b as x

HERE = Path(__file__).resolve().parent
ROWS = []
RUN = 'synthetic-distinct-run'
TR_SHA = 'a' * 64
DV_SHA = 'b' * 64


def record(name, kind, condition, detail=''):
    assert condition, name
    row = {'case': name, 'observation': kind, 'detail': detail}
    ROWS.append(row)
    print(json.dumps(row, sort_keys=True), flush=True)


def rejects(call, substring=None):
    try:
        call()
    except Exception as exc:
        if substring is not None:
            assert substring in str(exc), (substring, type(exc).__name__)
        return type(exc).__name__ if substring is None else substring
    raise AssertionError('Unexpected acceptance')


def fixture(n, label, rng):
    s = rng.normal(size=(n, 5))
    t = s @ W + rng.normal(size=(n, 7)) * 0.17
    r = t @ Q + rng.normal(size=(n, 8)) * 0.24
    ids = np.array([g.sha_bytes(f'{label}/{i}'.encode()) for i in range(n)])
    return dict(s=s, t=t, r=r, ids=ids)


def bind(fit):
    return dict(fit, schema='ttm.six.g1.fit_dev_frozen_v1b', run_id=RUN,
                manifest_sha256=g.MANIFEST_SHA, train_pack_sha256=TR_SHA, dev_pack_sha256=DV_SHA)


def auth():
    signing = Ed25519PrivateKey.generate()
    foreign = Ed25519PrivateKey.generate()
    # Test-only ephemeral keys, kept in RAM and never used by a CLI.
    pub = signing.public_key().public_bytes_raw()
    pin = g.sha_bytes(pub)
    expected = dict(phase='extract_TRAIN', workspace='fake-workspace', run_id=RUN,
                    reviewed_extractor_blob='a' * 40)
    body = dict(expected, schema='ttm.six.g1.owner_science_admission.v1b',
                decision='AUTHORIZE_G1_SCIENCE_ONE_SHOT', independent_review='PASS_DISTINCT_REVIEWER',
                manifest_sha256=g.MANIFEST_SHA, allow_private_numeric_feature_extraction=True,
                private_source_staging_approved=True, allow_one_shot_test=True,
                code_author_id='fixture-author', reviewer_id='fixture-reviewer',
                owner_id='fixture-owner', reviewed_core_blob='b' * 40,
                reviewed_amendment_blob='c' * 40, expires_unix=time.time()+300)
    def envelope(p, k=signing):
        return dict(payload=p, public_key_hex=k.public_key().public_bytes_raw().hex(),
                    signature_hex=k.sign(g.canonical(p)).hex())
    def verify(e):
        return g.verify_signed_permit(e, expected, authority_pin=pin)
    record('authority production disabled', 'CONTROL',
           rejects(lambda:g.verify_signed_permit(envelope(body), expected),
                   'AUTHORITY_KEY_NOT_PROVISIONED'))
    for field, val in [('phase','extract_TEST'), ('workspace','other'), ('run_id','wrong'),
                       ('reviewed_extractor_blob','0'*40)]:
        marker = 'PERMIT_FIELD_' + field.upper()
        record('signed wrong '+field, 'CONTROL',
               rejects(lambda:verify(envelope(dict(body, **{field:val}))), marker), marker)
    for label, b, err in [
        ('expired',dict(body,expires_unix=1),'PERMIT_EXPIRED'),
        ('same reviewer',dict(body,reviewer_id=body['code_author_id']),'PERMIT_NOT_DISTINCT'),
        ('missing author',{k:v for k,v in body.items() if k!='code_author_id'},'PERMIT_IDENTITY_OR_PIN_MISSING')]:
        record('authority '+label, 'CONTROL', rejects(lambda:verify(envelope(b)),err),err)
    record('authority foreign self-sign', 'CONTROL',
           rejects(lambda:verify(envelope(body,foreign)),'PERMIT_SIGNATURE_INVALID'))
    wrong_sig = envelope(body,foreign)
    wrong_sig['public_key_hex'] = pub.hex()
    record('authority foreign signature under pinned key', 'CONTROL',
           rejects(lambda:verify(wrong_sig),'PERMIT_SIGNATURE_INVALID'))
    unsigned = envelope(body)
    unsigned['payload'] = dict(body,phase='extract_TEST')
    record('authority modified after signing', 'CONTROL',
           rejects(lambda:verify(unsigned),'PERMIT_SIGNATURE_INVALID'))
    fake = dict(body, owner_id='self-claimed-other-owner', reviewer_id='self-claimed-other-reviewer',
                reviewed_core_blob='wrong-core', reviewed_amendment_blob='wrong-amendment')
    record('authority missing HEAD and weak cross-pins/identity binding', 'DEFECT',
           verify(envelope(fake))==fake, 'accepted synthetic signature with absent HEAD and scope detail')


def prep_checks():
    global FIT
    FIT = c.prepare(TR, DV)
    trr = TR['r']; mu = trr.mean(0)
    def scaled(a,b):
        std = np.maximum(np.std(a,axis=0),1e-6)
        return (a-a.mean(0))/std,(b-a.mean(0))/std
    s,sd = scaled(TR['s'], DV['s']); t,td = scaled(TR['t'], DV['t'])
    truth = DV['r']
    sst = ((truth-mu)**2).sum(0)
    def weights(z,y,a):
        return np.linalg.solve(z.T@z+a*np.eye(z.shape[1]),z.T@y)
    def pick(preds):
        return max((float(np.mean(1-((pred-truth)**2).sum(0)/sst)),a) for a,pred in preds)[1]
    p = pick((a,td@weights(t,trr-mu,a)+mu) for a in c.ALPHAS)
    tproj = t@weights(t,trr-mu,p)
    aligned = pick((a,sd@weights(s,tproj,a)+mu) for a in c.ALPHAS)
    direct = pick((a,sd@weights(s,trr-mu,a)+mu) for a in c.ALPHAS)
    perms = np.random.default_rng(20261110)
    digest = hashlib.sha256()
    alphas = []
    for _ in range(1000):
        ix = perms.permutation(128)
        digest.update(ix.astype('<i4').tobytes())
        alphas.append(pick((a,sd@weights(s,tproj[ix],a)+mu) for a in c.ALPHAS))
    record('independent primal DEV selection and all shuffled fits','CONTROL',
           (p,aligned,direct,alphas,digest.hexdigest()) ==
           (FIT['target_probe_alpha'],FIT['aligned_alpha'],FIT['direct_alpha'],
            FIT['null_alphas'],FIT['null_permutation_sha256']),
           {'null_fits':len(alphas),'alpha_histogram':{str(a):alphas.count(a) for a in c.ALPHAS},
            'permutation_sha256':digest.hexdigest()})
    ortho,_ = np.linalg.qr(np.random.default_rng(399).normal(size=(5,5)))
    baseline = sd@weights(s,tproj,aligned)
    rotation = (sd@ortho)@weights(s@ortho,tproj,aligned)
    record('orthogonal basis control after scaling','CONTROL',
           np.allclose(baseline,rotation,atol=1e-12),float(np.max(np.abs(baseline-rotation))))
    tr = dict(TR,r=np.zeros_like(TR['r']))
    dv = dict(DV,r=np.repeat(trr.mean(0)[None,:],64,axis=0))
    for label, args, err in [
        ('TRAIN zero probe standard deviation',(tr,DV),'TRAIN_FUNCTION_STD_DEGENERATE'),
        ('DEV zero SST',(TR,dv),'DEV_SST_DEGENERATE')]:
        record(label,'CONTROL',rejects(lambda:c.prepare(*args),err),err)
    record('invalid alpha','CONTROL',rejects(lambda:c.dual_predict(np.ones(1),np.ones((1,1)),
           np.ones((1,1)),np.ones((1,1)),np.ones((1,1)),2),'ALPHA_NOT_FROZEN'))
    record('wrong permutation count','CONTROL',
           rejects(lambda:c.evaluate(TR,DV,TE,FIT,permutation_n=999),'NULL_COUNT_PIN'))
    result = c.evaluate(TR,DV,TE,FIT)
    record('full synthetic evaluate counts','CONTROL',
           (result['null_count'],result['cka_null_count'],result['bootstrap_count'])==(1000,1000,2000),
           {k:result[k] for k in ('aligned_macro_r2','direct_macro_r2','oracle_macro_r2',
               'permutation_p','cka_permutation_p','bootstrap_95_lower_aligned_minus_mean')})
    dz = dict(TE,r=np.repeat(trr.mean(0)[None,:],64,axis=0))
    record('full synthetic zero TEST SST','CONTROL',
           c.evaluate(TR,DV,dz,FIT)['verdict']=='INCONCLUSIVE_DEGENERATE_TEST')
    dz = dict(TE,s=np.zeros_like(TE['s']))
    record('full synthetic zero CKA','CONTROL',
           c.evaluate(TR,DV,dz,FIT)['verdict']=='INCONCLUSIVE_GEOMETRY_DEGENERATE')
    zero = np.zeros((64,8)); spike = zero.copy(); spike[-1] = 1
    boot = g.stable_bootstrap_delta(spike,spike,np.zeros(8))
    ix = np.random.default_rng(20261111).integers(0,64,size=(2000,64))
    zero_draws = int(np.sum(np.all(ix!=63,axis=1)))
    record('63+1 bootstrap includes zero-deviation draws','CONTROL',
           boot['bootstrap_lower']==0 and zero_draws>0,
           {'zero_deviation_draws':zero_draws,'lower':boot['bootstrap_lower']})


def zip_bytes(values, oversized=False, ratio_bomb=False):
    buf = io.BytesIO()
    if oversized or ratio_bomb:
        with zipfile.ZipFile(buf,'w',compression=zipfile.ZIP_DEFLATED) as z:
            size = g.MAX_MEMBER_BYTES+1 if oversized else 2*1024*1024
            z.writestr('s.npy', b'X'*size)
            for key in ('ids.npy','t.npy','r.npy'):
                z.writestr(key,b'X')
    else:
        np.savez_compressed(buf,**values)
    return buf.getvalue()


def receipt(raw):
    return dict(schema='ttm.six.g1.feature_pack_commit.v1b',status='PACK_COMMITTED',
                split='DEV',run_id=RUN,manifest_sha256=g.MANIFEST_SHA,sha256=g.sha_bytes(raw))


def pack_checks(root):
    manifest = {'splits':{'DEV':[{'source_story_sha256':s} for s in DV['ids'].tolist()]}}
    p = root/'fixture.npz'; q = p.with_suffix('.receipt.json')
    original = zip_bytes(DV)
    mutation = copy.deepcopy(DV)
    mutation['s'][13,2] += 0.25
    changed = zip_bytes(mutation)
    def read(expected):
        return c.load_pack(p,'DEV',manifest,5,7,run_id=RUN,root=root,trusted_pack_sha=expected)
    p.write_bytes(changed); q.write_bytes(g.canonical(receipt(changed)))
    record('NPZ tensor mutation with same IDs and matching self-written receipt','CONTROL',
           rejects(lambda:read(g.sha_bytes(original)),'TRUSTED_PACK_SHA_MISMATCH'))
    p.write_bytes(original); q.write_bytes(g.canonical(receipt(original)))
    original_reader = g.read_private_bytes
    opens = []
    def replace_after_read(path,*args,**kwargs):
        data = original_reader(path,*args,**kwargs)
        if Path(path)==p:
            opens.append(path)
            p.write_bytes(changed)
        return data
    with patch.object(g,'read_private_bytes',replace_after_read):
        checked = read(g.sha_bytes(original))
    record('hash and parse same buffer despite post-read substitution','CONTROL',
           len(opens)==1 and np.array_equal(checked['s'],DV['s']))
    for label,raw,reason in [
        ('oversize member',zip_bytes(DV,oversized=True),'PACK_MEMBER_SIZE'),
        ('ZIP bomb compression ratio',zip_bytes(DV,ratio_bomb=True),'PACK_COMPRESSION_RATIO')]:
        record(label,'CONTROL',rejects(lambda:g.parse_authenticated_pack(raw,receipt(raw),
               split='DEV',manifest=manifest,run_id=RUN,source_dim=5,target_dim=7),reason),reason)
    # Real Windows directory junction, confined to this synthetic root.
    target = root/'junction_target'; target.mkdir()
    (target/'sentinel.bin').write_bytes(b'fixture')
    jump = root/'junction'
    proc = subprocess.run(['cmd.exe','/d','/c','mklink','/J',str(jump),str(target)],
                          capture_output=True,check=False)
    if proc.returncode:
        record('Windows junction','NOT_TESTED',True,proc.returncode)
    else:
        try:
            record('Windows junction rejected','CONTROL',
                   rejects(lambda:g.read_private_bytes(jump/'sentinel.bin',root),'PATH_SYMLINK'))
            # A redirect in the private root itself is checked only after the write.
            inside = jump/'misdirected.bin'
            record('commit through junction root writes before rejecting','DEFECT',
                   rejects(lambda:g.commit_immutable_bytes(inside,b'fixture',jump),'PATH_SYMLINK')
                   and (target/'misdirected.bin').read_bytes()==b'fixture')
        finally:
            os.rmdir(jump)
    symlink = root/'symbolic.bin'
    try:
        symlink.symlink_to(target/'sentinel.bin')
    except OSError as e:
        record('Windows symbolic link','NOT_TESTED',True,e.winerror)
    else:
        record('Windows symbolic link rejected','CONTROL',
               rejects(lambda:g.read_private_bytes(symlink,root),'PATH_SYMLINK'))
        symlink.unlink()
    # Simulated swap at the check/open boundary with two real files.
    actual_open = os.open
    with patch.object(g.os,'open',lambda path,flags:actual_open(target/'sentinel.bin',flags)):
        record('read handle not tied to prechecked path identity','DEFECT',
               g.read_private_bytes(p,root)==b'fixture',
               'mock redirect at os.open; trusted NPZ digest independently detects byte change')


def one_shot(root):
    mk = root/'worker.marker'
    def claim():
        try:
            with mk.open('x') as fd:
                fd.write('fixture');fd.flush();os.fsync(fd.fileno())
            return True
        except FileExistsError:
            return False
    with ThreadPoolExecutor(8) as pool:
        wins = sum(pool.map(lambda _:claim(),range(8)))
    record('8 concurrent exclusive marker claimants','CONTROL',wins==1,{'wins':wins})
    mk.unlink()
    record('workspace rollback/deleted marker replays after consumption','DEFECT',claim())
    p = root/'crash-pack.npz'; receipt_path = root/'crash-pack.receipt.json'
    with patch.object(g.os,'link',side_effect=OSError('fixture before link')):
        record('crash before pack link leaves no final pack','CONTROL',
               rejects(lambda:g.commit_immutable_bytes(p,b'a',root),'COMMIT_ATOMIC_LINK_FAILED')
               and not p.exists())
    def after_link(path,*args,**kwargs):
        raise RuntimeError('fixture after link')
    with patch.object(g,'read_private_bytes',after_link):
        record('crash after pack link leaves pack without receipt','DEFECT',
               rejects(lambda:g.commit_immutable_bytes(p,b'content',root),'fixture after link')
               and p.read_bytes()==b'content' and not receipt_path.exists())
    with patch.object(g.os,'link',side_effect=OSError('fixture before receipt link')):
        record('crash before receipt publication leaves orphan','DEFECT',
               rejects(lambda:g.commit_immutable_bytes(receipt_path,b'{}',root),'COMMIT_ATOMIC_LINK_FAILED')
               and p.exists() and not receipt_path.exists())
    with patch.object(g,'read_private_bytes',after_link):
        record('crash after receipt publication leaves both bytes','CONTROL',
               rejects(lambda:g.commit_immutable_bytes(receipt_path,b'{}',root),'fixture after link')
               and p.exists() and receipt_path.read_bytes()==b'{}')


def split_and_entrypoints(root):
    work = root/'ttm_six_g1_science_private'; work.mkdir()
    permit = root/'synthetic-empty.json'; permit.write_text('{}')
    p = work/'G1_FIT_DEV_FROZEN.json'
    frozen = bind(FIT); encoded = c.jbytes(frozen)
    signed_fixture = {'fit_sha256':g.sha_bytes(encoded),'pack_sha_by_split':
                      {'TRAIN':TR_SHA,'DEV':DV_SHA,'TEST':'c'*64}}
    minimal = {k:v for k,v in frozen.items() if k not in
               {'seed_shuffle','seed_cka','seed_boot','control_oracle_dev_macro_r2'}}
    minimal['null_alphas'] = [True]*1000
    minimal['null_permutation_sha256'] = '?'*64
    raw = c.jbytes(minimal)
    record('malformed complete freeze accepted by extractor validator','DEFECT',
           g.validate_frozen_dev(raw,g.sha_bytes(raw),TR_SHA,DV_SHA,run_id=RUN)==minimal,
           'boolean alpha and non-hex digest accepted; seeds omitted')
    manifest = {'counts':g.COUNTS,'splits':{'TRAIN':[],'DEV':[],'TEST':[]}}
    base_read_text = Path.read_text
    def read_metadata(path,*args,**kwargs):
        if path==work/'G1_PREFIX_IDS_128_64_64_PRIVATE_METADATA.json':
            return json.dumps(manifest)
        return base_read_text(path,*args,**kwargs)
    argv = ['extractor','--mode','extract','--split','TEST','--private-root',str(root),
            '--permit',str(permit),'--run-id',RUN]
    with contextlib.ExitStack() as stack:
        use = stack.enter_context
        use(patch.object(sys,'argv',argv))
        use(patch.object(x,'sha_file',return_value=x.MANIFEST_SHA))
        use(patch.object(Path,'read_text',read_metadata))
        env = use(patch.object(x,'environment',side_effect=AssertionError('GPU TRAP')))
        read = use(patch.object(x,'reconstruct',side_effect=AssertionError('SOURCE TRAP')))
        record('extractor production permit blocks before GPU or source','CONTROL',
               rejects(x.main,'AUTHORITY_KEY_NOT_PROVISIONED') and not env.called and not read.called)
        use(patch.object(x,'check_permit',return_value=signed_fixture))
        record('missing freeze before GPU or source','CONTROL',
               rejects(x.main,'PATH_NOT_REGULAR_FILE') and not env.called and not read.called)
        p.write_bytes(b'')
        record('empty freeze before GPU or source','CONTROL',
               rejects(x.main,'FIT_DEV_HASH_CHANGED') and not env.called and not read.called)
        p.write_bytes(encoded+b' ')
        record('changed freeze before GPU or source','CONTROL',
               rejects(x.main,'FIT_DEV_HASH_CHANGED') and not env.called and not read.called)
        wrong = c.jbytes(dict(frozen,run_id='other'))
        p.write_bytes(wrong)
        with patch.dict(signed_fixture,fit_sha256=g.sha_bytes(wrong)):
            record('authentic digest but wrong freeze run','CONTROL',
                   rejects(x.main,'FIT_DEV_FIELD_RUN_ID') and not env.called and not read.called)
        p.write_bytes(encoded)
        marker = work/'G1_EXTRACT_TEST_ONE_SHOT_CONSUMED.marker'
        with patch.object(x,'environment',side_effect=RuntimeError('fixture before marker')):
            record('extractor crash before marker leaves source unopened','CONTROL',
                   rejects(x.main,'fixture before marker') and not marker.exists() and not read.called)
        def after_marker(*args,**kwargs):
            assert marker.read_bytes().startswith(b'EXTRACTION_CONSUMED')
            raise RuntimeError('fixture at TEST read boundary')
        with patch.object(x,'environment',return_value=object()), patch.object(x,'reconstruct',after_marker):
            record('extractor fault after marker before TEST bytes','CONTROL',
                   rejects(x.main,'fixture at TEST read boundary') and marker.exists())
            record('extractor STOP blocks replay while marker persists','CONTROL',
                   rejects(x.main,'EXTRACTION_ALREADY_CONSUMED'))
            marker.unlink()
            record('extractor replay after workspace marker deletion','DEFECT',
                   rejects(x.main,'fixture at TEST read boundary'))
    paths = []
    def only_synthetic(path,*args,**kwargs):
        paths.append(Path(path).name)
        if Path(path).name not in {'G1_PREFIX_TRAIN.json','G1_PREFIX_DEV.json'}:
            raise AssertionError('TEST/full corpus open trap')
        n = 128 if Path(path).name=='G1_PREFIX_TRAIN.json' else 64
        split = 'TRAIN' if n==128 else 'DEV'
        return g.canonical(dict(schema='ttm.six.g1.private_split_prefix_v1b',split=split,
                                manifest_sha256=g.MANIFEST_SHA, rows=payloads[split]))
    fake = 'synthetic prefix, no private data'
    payloads = {}
    for split,n in [('TRAIN',128),('DEV',64)]:
        payloads[split] = [{'source_story_sha256':g.sha_bytes(f'{split}{i}'.encode()),'prefix':fake}
                           for i in range(n)]
        manifest['splits'][split] = [dict(r,prefix_end_unicode_codepoint_offset=len(fake),
                                        normalized_prefix_utf8_sha256=g.sha_bytes(fake.encode()))
                                    for r in payloads[split]]
    with patch.object(g,'read_private_bytes',only_synthetic):
        assert len(x.reconstruct(manifest,'TRAIN',root))==128
        assert len(x.reconstruct(manifest,'DEV',root))==64
        assert rejects(lambda:x.
...[cắt bớt 13570 ký tự]