#!/usr/bin/env python3
"""G1 v1b pre-execution security and inference guard. No model or dataset imports.

This module is review-candidate code; all real science is DENIED until an externally
provisioned Ed25519 authority key fingerprint is frozen in a later reviewed release.
"""
from __future__ import annotations
import hashlib, io, json, os, stat, struct, time, uuid, zipfile
from pathlib import Path
import numpy as np

MANIFEST_SHA = '6451be0cd09a54378eda9e815b5c89ce8ce8301ddefef556476d94e3e31e42b6'
T1_SHA = '9f2ebaca821bddf0a9d7ae30ccfcef34561b968b21159aa913794298235a2fa9'
COUNTS = {'TRAIN': 128, 'DEV': 64, 'TEST': 64}
# This value has NOT been provisioned by owner. A blank pin is a non-bypassable HOLD.
OWNER_ED25519_PUBLIC_SHA256_PIN: str | None = None
MAX_PACK_BYTES = 12 * 1024 * 1024
MAX_MEMBER_BYTES = 4 * 1024 * 1024
MAX_NUMPY_ELEMENTS = 128 * 2048
ALLOWED_KEYS = {'ids.npy', 's.npy', 't.npy', 'r.npy'}


def stop(code):
    raise RuntimeError('STOP_G1_' + code)


def require(ok, code):
    if not ok:
        stop(code)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def verify_signed_permit(envelope, expected, *, authority_pin=OWNER_ED25519_PUBLIC_SHA256_PIN):
    """Detached Ed25519 signature on canonical permit payload; never trust JSON flags.

    Independent negative tests can pass a synthetic pinned public-key fingerprint;
    production must use OWNER_ED25519_PUBLIC_SHA256_PIN (=None while HOLD).
    """
    require(isinstance(authority_pin, str) and len(authority_pin) == 64,
            'AUTHORITY_KEY_NOT_PROVISIONED')
    require(set(envelope) == {'payload','public_key_hex','signature_hex'},
            'PERMIT_ENVELOPE_FIELDS')
    try:
        keybytes = bytes.fromhex(envelope['public_key_hex'])
        signature = bytes.fromhex(envelope['signature_hex'])
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        require(len(keybytes)==32 and len(signature)==64, 'PERMIT_KEY_SIGNATURE_SIZE')
        require(sha_bytes(keybytes)==authority_pin, 'PERMIT_AUTHORITY_KEY_MISMATCH')
        Ed25519PublicKey.from_public_bytes(keybytes).verify(signature,canonical(envelope['payload']))
    except (ValueError, TypeError, KeyError, AttributeError, ImportError) as exc:
        stop('PERMIT_MALFORMED')
    except Exception:
        stop('PERMIT_SIGNATURE_INVALID')
    p=envelope['payload']
    required={
      'schema':'ttm.six.g1.owner_science_admission.v1b',
      'decision':'AUTHORIZE_G1_SCIENCE_ONE_SHOT',
      'independent_review':'PASS_DISTINCT_REVIEWER',
      'manifest_sha256':MANIFEST_SHA,
      'allow_private_numeric_feature_extraction':True,
      'private_source_staging_approved':True,
      'allow_one_shot_test':True,
    }
    for key,value in {**required,**expected}.items():
        require(p.get(key)==value,'PERMIT_FIELD_'+key.upper())
    names=('run_id','workspace','code_author_id','reviewer_id',
           'reviewed_core_blob','reviewed_extractor_blob','reviewed_amendment_blob',
           'owner_id','expires_unix')
    require(all(p.get(k) for k in names),'PERMIT_IDENTITY_OR_PIN_MISSING')
    require(p['code_author_id']!=p['reviewer_id'],'PERMIT_NOT_DISTINCT')
    require(time.time()<int(p['expires_unix']),'PERMIT_EXPIRED')
    return p


def ensure_regular_no_redirect(path, private_root):
    """Reject each symlink / Windows junction component inside private scope.

    Caller must use read_private_bytes for handle-bounded reads. OS ACL must
    prevent an untrusted same-user actor from swapping parent directories.
    """
    p=Path(path).absolute(); root=Path(private_root).absolute()
    require(p == root or root in p.parents, 'PATH_OUTSIDE_PRIVATE_ROOT')
    cur=root
    chain=[root]
    for name in p.relative_to(root).parts:
        cur=cur/name
        chain.append(cur)
    for item in chain:
        if item.exists() or item.is_symlink():
            require(not item.is_symlink() and
                    not getattr(os.path, 'isjunction', lambda x: False)(item),
                    'PATH_SYMLINK')
            st=item.lstat()
            require(not stat.S_ISLNK(st.st_mode), 'PATH_REPARSE_OR_LINK')
    require(p.is_file() and stat.S_ISREG(p.stat().st_mode),
            'PATH_NOT_REGULAR_FILE')
    return p


def read_private_bytes(path, root, max_size=MAX_PACK_BYTES):
    """Read one verified OS file handle once, without a second path open."""
    p=ensure_regular_no_redirect(path,root)
    flags=os.O_RDONLY|getattr(os, 'O_BINARY', 0)
    if hasattr(os, 'O_NOFOLLOW'):
        flags |= os.O_NOFOLLOW
    fd=os.open(str(p),flags)
    try:
        st=os.fstat(fd)
        require(stat.S_ISREG(st.st_mode) and st.st_size<=max_size,
                'PACK_FD_TYPE_OR_SIZE')
        with os.fdopen(fd,'rb',closefd=False) as f:
            payload=f.read(max_size+1)
        require(len(payload)<=max_size,'PACK_READ_OVERSIZE')
        return payload
    finally:
        os.close(fd)



def commit_immutable_bytes(path, data, root):
    """Write-complete then atomically publish via exclusive hardlink; never overwrite.

    An interrupted staging file remains for forensic review. A failed stage is
    terminal under the one-shot marker, not a permit for automatic replay.
    """
    p=Path(path).absolute();priv=Path(root).absolute()
    require(priv in p.parents and p.parent.is_dir(),'COMMIT_OUTSIDE_SCOPE')
    # Verify every parent is not a symlink or Windows junction.
    cur=priv
    for part in p.relative_to(priv).parts[:-1]:
        cur=cur/part
        require(not cur.is_symlink() and
                not getattr(os.path,'isjunction',lambda _:False)(cur),
                'COMMIT_PARENT_REDIRECT')
    require(not p.exists() and not p.is_symlink(),'COMMIT_TARGET_EXISTS')
    stage=p.with_name(p.name+'.staging.'+uuid.uuid4().hex)
    require(not stage.exists(),'COMMIT_STAGE_EXISTS')
    with stage.open('xb') as f:
        f.write(data);f.flush();os.fsync(f.fileno())
    try:
        # os.link raises FileExistsError and never silently replaces a target.
        os.link(stage,p,follow_symlinks=False)
    except (OSError,NotImplementedError):
        stop('COMMIT_ATOMIC_LINK_FAILED')
    stage.unlink()
    require(sha_bytes(read_private_bytes(p,root,max_size=max(len(data),1)+1))
            ==sha_bytes(data),'COMMIT_POST_SHA')
    return sha_bytes(data)


def _check_array_headers(data, split, source_dim=1024, target_dim=2048):
    required={'ids.npy': ('U', (COUNTS[split],)),
              's.npy': ('f',(COUNTS[split],source_dim)),
              't.npy': ('f',(COUNTS[split],target_dim)),
              'r.npy': ('f',(COUNTS[split],8))}
    with zipfile.ZipFile(io.BytesIO(data),'r') as z:
        names=z.namelist()
        require(len(names)==4 and set(names)==ALLOWED_KEYS,'PACK_MEMBER_SCHEMA')
        total=0
        for name in names:
            info=z.getinfo(name)
            require(info.file_size<=MAX_MEMBER_BYTES,'PACK_MEMBER_SIZE')
            require(info.compress_size>0 and info.file_size<=max(4096,info.compress_size*1000),
                    'PACK_COMPRESSION_RATIO')
            total += info.file_size
            with z.open(name,'r') as fd:
                magic=fd.read(8)
                require(magic==b'\x93NUMPY\x01\x00' or magic==b'\x93NUMPY\x02\x00',
                        'PACK_NOT_NUMPY')
                lsize=2 if magic.endswith(b'\x01\x00') else 4
                hlen=int.from_bytes(fd.read(lsize),'little')
                require(0<hlen<=32768,'PACK_HEADER_SIZE')
                import ast
                head=ast.literal_eval(fd.read(hlen).decode('latin-1').strip())
                require(isinstance(head,dict) and set(head)=={'descr','fortran_order','shape'},
                        'PACK_HEADER_KEYS')
                dt=np.dtype(head['descr'])
                require(dt.kind==required[name][0] and tuple(head['shape'])==required[name][1]
                        and not head['fortran_order'],'PACK_HEADER_SHAPE_DTYPE')
                require(dt.kind not in {'O','V'},'PACK_OBJECT_DTYPE')
        require(total<MAX_PACK_BYTES,'PACK_UNCOMPRESSED_TOTAL')
    return True


def parse_authenticated_pack(raw_bytes, receipt, *, split, manifest, run_id,
                             source_dim=1024,target_dim=2048):
    """Hash and parse the *same bytes*; receipt must arrive through trusted state.

    Merely self-supplied, unsigned receipt JSON does NOT establish authenticity.
    """
    require(len(raw_bytes)<=MAX_PACK_BYTES,'PACK_OVERSIZE')
    require(receipt.get('schema')=='ttm.six.g1.feature_pack_commit.v1b','PACK_RECEIPT_SCHEMA')
    require(receipt.get('status')=='PACK_COMMITTED','PACK_NOT_COMMITTED')
    for field,value in {'split':split,'run_id':run_id,'manifest_sha256':MANIFEST_SHA,
                        'sha256':sha_bytes(raw_bytes)}.items():
        require(receipt.get(field)==value,'PACK_RECEIPT_'+field.upper())
    _check_array_headers(raw_bytes,split,source_dim,target_dim)
    with np.load(io.BytesIO(raw_bytes),allow_pickle=False) as z:
        pack={k:z[k] for k in ('ids','s','t','r')}
    expids=[x['source_story_sha256'] for x in manifest['splits'][split]]
    ids=pack['ids'].tolist()
    require(ids==expids,'PACK_MANIFEST_IDS_CHANGED')
    for key in ('s','t','r'):
        require(np.isfinite(pack[key]).all(),'PACK_NONFINITE_'+key)
    return pack


def validate_frozen_dev(freeze_bytes, digest, train_pack_sha, dev_pack_sha, *, run_id):
    require(sha_bytes(freeze_bytes)==digest,'FIT_DEV_HASH_CHANGED')
    try: freeze=json.loads(freeze_bytes)
    except (TypeError,ValueError):stop('FIT_DEV_JSON_INVALID')
    required={'schema':'ttm.six.g1.fit_dev_frozen_v1b',
              'manifest_sha256':MANIFEST_SHA,'run_id':run_id,
              'train_pack_sha256':train_pack_sha,'dev_pack_sha256':dev_pack_sha,
              'test_touched':False,'null_count':1000,'primary_layer':28,'function_count':8}
    for key,value in required.items():
        require(freeze.get(key)==value,'FIT_DEV_FIELD_'+key.upper())
    alpha=(1.,10.,100.)
    for k in ('aligned_alpha','direct_alpha','target_probe_alpha'):
        require(type(freeze.get(k)) in (float,int) and freeze[k] in alpha,'FIT_DEV_ALPHA')
    alphas=freeze.get('null_alphas')
    require(isinstance(alphas,list) and len(alphas)==1000 and all(x in alpha for x in alphas),
            'FIT_DEV_NULL_GRID')
    require(isinstance(freeze.get('null_permutation_sha256'),str) and
            len(freeze['null_permutation_sha256'])==64,'FIT_DEV_NULL_SHA')
    return freeze


def open_split_payload(split, freeze_validated, split_source_root):
    """No original TinyStories full-corpus scanner in the science runner.

    Staging is a *separate owner-authorized action* not provided by this module;
    the science runtime opens only a pre-split source after freeze for TEST.
    """
    require(split in COUNTS,'SPLIT_INVALID')
    require(split!='TEST' or freeze_validated,'TEST_PREMATURE_SOURCE_ACCESS')
    path=Path(split_source_root)/('G1_PREFIX_'+split+'.json')
    return read_private_bytes(path,split_source_root,max_size=2*1024*1024)


class Budget:
    def __init__(self, previous, clock=time.monotonic):
        self.clock=clock
        self.begin=self.clock()
        self.elapsed={'source':float(previous.get('source',0.)),
                      'target':float(previous.get('target',0.))}
        require(all(x>=0 for x in self.elapsed.values()),'BUDGET_BAD_LEDGER')
        require(sum(self.elapsed.values())<=7200,'BUDGET_PREVIOUS_OVERRUN')

    def check(self, name, began):
        require(name in ('source','target'),'BUDGET_UNKNOWN_MODEL')
        elapsed=self.elapsed[name]+self.clock()-began
        require(elapsed<=3600,'MODEL_CUMULATIVE_TIMEOUT')
        total=sum(self.elapsed.values())+self.clock()-began
        require(total<=7200,'RUN_CUMULATIVE_TIMEOUT')
        return elapsed

    def finish(self, name, began):
        self.check(name,began)
        self.elapsed[name]+=self.clock()-began
        return self.elapsed.copy()


def stable_bootstrap_delta(pred, truth, train_mean, *, n=2000, seed=20261111):
    """Paired improvement over TRAIN mean; denominator frozen at full TEST SST.

    This deliberately amends the v1 bootstrap estimand and needs distinct review.
    """
    truth=np.asarray(truth,dtype=np.float64)
    pred=np.asarray(pred,dtype=np.float64)
    mean=np.asarray(train_mean,dtype=np.float64)
    require(truth.shape==(64,8) and pred.shape==(64,8) and mean.shape==(8,),
            'BOOT_SHAPE')
    sst=((truth-mean)**2).sum(axis=0)
    if (sst<1e-8).any():
        return {'status':'INCONCLUSIVE_DEGENERATE_TEST','bootstrap_lower':None}
    dif=(truth-mean)**2-(truth-pred)**2
    rng=np.random.default_rng(seed)
    samples=np.empty(n,dtype=np.float64)
    for i in range(n):
        ix=rng.integers(0,64,size=64)
        samples[i]=float((dif[ix].sum(axis=0)/sst).mean())
    require(np.isfinite(samples).all(),'BOOT_NONFINITE')
    return {'status':'PASS_STATISTICS_VALID',
            'bootstrap_lower':float(np.quantile(samples,0.025)),
            'bootstrap_estimand':'paired_improvement_vs_train_mean_fixed_full_TEST_SST'}


def safe_cka(a,b):
    a=np.asarray(a,dtype=np.float64);b=np.asarray(b,dtype=np.float64)
    x=a-a.mean(axis=0); y=b-b.mean(axis=0)
    gx=x@x.T;gy=y@y.T
    den=np.linalg.norm(gx)*np.linalg.norm(gy)
    if den<1e-15:return {'status':'INCONCLUSIVE_GEOMETRY_DEGENERATE','cka':None}
    return {'status':'PASS_CKA','cka':float((gx*gy).sum()/den)}


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['selftest'],required=True)
    p.parse_args()
    print(json.dumps({'status':'V1B_GUARD_SOURCE_ONLY_NO_SCIENCE',
        'owner_key_provisioned': OWNER_ED25519_PUBLIC_SHA256_PIN is not None,
        'science_authorized':False},sort_keys=True))
