#!/usr/bin/env python3
"""TTM-SM4M-DIAG-Q001: a fail-closed, *candidate* one-shot CPU diagnostic.

source-qa runs only stdlib in-memory MOCK oracle tests. It does not access a
checkpoint or produce real study fixtures. `run` requires approved external
permit, distinct independent review, the private model, and tokenizer custody.
Do not treat this local candidate as an authorized I1 implementation.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import random
import sys
import time

QID = 'TTM-SM4M-DIAG-Q001'
SOURCE_BLOB = '9762343e06cf800b50574c2871ae1ed58537fb18'
MODEL_SHA = 'cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b'
RELEASE_GUARD_GIT_BLOB = '66461481f05c19b89f7ae928719dd78b7db2768c'
MODEL_SIZE = 45074891
MODEL_CONFIG = dict(vocab_size=2048, max_seq_len=256, n_embd=256,
                    n_layer=4, n_head=4, norm_type='layernorm')
SEED = 20261116
GROUPS = dict(TRAIN=24, HELDOUT_RECOMBINED=16, HELDOUT_NOVEL_IDS=16,
              PAIRED_COUNTERFACTUAL=16, HELDOUT_ABSENT=8)
MAX_STEPS = 256
WALL_SECONDS = 900
MEMORY_BYTES = 12 * 1024**3
OUTPUT_BYTES = 1024**3


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def git_blob(path: Path) -> str:
    raw = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def stop(reason: str) -> None:
    raise RuntimeError('HOLD_' + reason)


def json_bytes(x: object) -> bytes:
    return (json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')


def json_read(path: Path) -> dict:
    data = json.loads(path.read_text('utf-8'))
    if not isinstance(data, dict):
        stop('JSON_SCHEMA')
    return data


def permitted_ids(meta: dict, underlying_bytes: bytes) -> list[int]:
    """Verify *actual original inventory bytes* and full 2048-ID taxonomy.

    Underlying inventory is a custody-supplied normalized export, not a value
    invented from this runner. Only after independently signed rights admission
    may a real inventory be opened. Source QA passes in-memory MOCK bytes only.
    """
    if meta.get('schema') != 'ttm.sm4m.diag.tokenizer_allowed_ids.v1':
        stop('TOKENIZER_SCHEMA')
    if meta.get('vocab_size') != 2048:
        stop('TOKENIZER_VOCAB')
    sh = meta.get('underlying_inventory_sha256')
    if not isinstance(sh, str) or len(sh) != 64 or any(c not in '0123456789abcdef' for c in sh):
        stop('TOKENIZER_UNDERLYING_SHA256_FORMAT')
    if hashlib.sha256(underlying_bytes).hexdigest() != sh:
        stop('TOKENIZER_SOURCE_SHA_MISMATCH')
    try:
        full = json.loads(underlying_bytes)
    except (ValueError, UnicodeDecodeError):
        stop('TOKENIZER_SOURCE_BAD_JSON')
    if not isinstance(full, dict) or full.get('schema') != 'ttm.sm4m.diag.tokenizer_full_inventory.v1' or full.get('vocab_size') != 2048:
        stop('TOKENIZER_SOURCE_SCHEMA')
    ids, reserved, special = (meta.get('allowed_non_special_ids'),
                             meta.get('reserved_ids'), full.get('special_ids'))
    source_allowed = full.get('non_special_token_ids')
    if not all(isinstance(x, list) for x in (ids, reserved, special, source_allowed)):
        stop('TOKENIZER_ID_LIST')
    for lst in (ids, reserved, special, source_allowed):
        if any(type(x) is not int or not (0 <= x < 2048) for x in lst) or len(set(lst)) != len(lst):
            stop('TOKENIZER_ID_RANGE_DUPLICATE')
    if (len(ids) < 80 or set(ids) & set(reserved) or set(ids) & set(special)
            or set(reserved) & set(special) or set(ids) != set(source_allowed)
            or set(ids) | set(reserved) | set(special) != set(range(2048))):
        stop('TOKENIZER_TAXONOMY_OR_CUSTODY')
    if meta.get('reserved_ids') != full.get('reserved_ids'):
        stop('TOKENIZER_RESERVED_MISMATCH')
    return ids


def mock_token_inventory() -> tuple[dict, bytes]:
    """Generated in memory for MOCK QA; never an admitted tokenizer source."""
    ids = list(range(100, 300))
    reserved = list(range(100)) + list(range(300, 2048))
    inv = dict(schema='ttm.sm4m.diag.tokenizer_full_inventory.v1',
               vocab_size=2048, non_special_token_ids=ids,
               special_ids=[], reserved_ids=reserved)
    raw = json_bytes(inv)
    meta = dict(schema='ttm.sm4m.diag.tokenizer_allowed_ids.v1',
                vocab_size=2048, allowed_non_special_ids=ids,
                reserved_ids=reserved, underlying_inventory_sha256=hashlib.sha256(raw).hexdigest())
    return meta, raw

def fixture_generator(allowed: list[int], seed: int = SEED) -> list[dict]:
    """Pure in-memory deterministic generator; *not* an authorization to run.

    Only call with verified allowed token-ID metadata for an admitted I1/I2;
    source-qa calls it with a mock inventory that never leaves process memory.
    """
    rng = random.Random(seed)
    pool = allowed[:]
    if len(pool) != len(set(pool)) or len(pool) < 80:
        stop('TOKEN_POOL_INVALID')
    rng.shuffle(pool)
    bind, query, answer, no_answer = pool[:4]
    keys_seen = pool[4:20]
    vals_seen = pool[20:36]
    keys_novel = pool[36:52]
    vals_novel = pool[52:68]
    roles = [bind, query, answer, no_answer]
    if len(set(roles + keys_seen + vals_seen + keys_novel + vals_novel)) != 68:
        stop('TOKEN_ROLE_OVERLAP')
    rows: list[dict] = []
    seen_contexts: set[tuple[int, ...]] = set()

    def put(group: str, k1: int, v1: int, k2: int, v2: int, kq: int,
            parent: str | None = None):
        if k1 == k2 or v1 == v2 or k1 == kq and k2 == kq:
            stop('BAD_CASE')
        ctx = (bind, k1, v1, bind, k2, v2, query, kq, answer)
        if ctx in seen_contexts:
            return False
        gold = v1 if kq == k1 else (v2 if kq == k2 else no_answer)
        row = dict(group=group, id=f'{group}_{sum(x["group"] == group for x in rows):02d}',
                   context=list(ctx), gold=gold, first_value=v1, second_value=v2,
                   query_position=1 if kq == k1 else 2 if kq == k2 else 0,
                   parent=parent)
        # Candidate set defined from a frozen pool, never from model logits.
        distract = [no_answer] + sorted(set(vals_seen + vals_novel))
        # Distinct fixed 4-way choices, independent of the model's outputs.
        opts = [gold]
        for candidate in distract:
            if candidate != gold and candidate not in opts:
                opts.append(candidate)
            if len(opts) == 4:
                break
        if len(opts) != 4:
            stop('INSUFFICIENT_CHOICES')
        row['choices'] = opts
        seen_contexts.add(ctx)
        rows.append(row)
        return True

    # 16 bound cases, half query first, half query second.
    for i in range(16):
        k1 = keys_seen[i]
        k2 = keys_seen[(i + 5) % len(keys_seen)]
        v1 = vals_seen[i]
        v2 = vals_seen[(i + 7) % len(vals_seen)]
        q = k1 if i % 2 == 0 else k2
        assert put('TRAIN', k1, v1, k2, v2, q)
    # 8 absent queries; use seen key pool but query key absent from both bindings.
    for i in range(8):
        k1, k2, kq = keys_seen[i], keys_seen[(i + 3) % 16], keys_seen[(i + 8) % 16]
        v1, v2 = vals_seen[i], vals_seen[(i + 4) % 16]
        assert put('TRAIN', k1, v1, k2, v2, kq)

    # Novel combinations of ONLY symbols already seen in probe TRAIN.
    trial = 0
    while sum(x['group'] == 'HELDOUT_RECOMBINED' for x in rows) < 16:
        trial += 1
        if trial > 10000:
            stop('NO_UNIQUE_RECOMBINED')
        k1, k2 = rng.sample(keys_seen, 2)
        v1, v2 = rng.sample(vals_seen, 2)
        q = k1 if trial % 2 else k2
        put('HELDOUT_RECOMBINED', k1, v1, k2, v2, q)
    # New keys AND new values, unseen in probe TRAIN, NOT necessarily pretraining.
    for i in range(16):
        k1, k2 = keys_novel[i], keys_novel[(i + 1) % 16]
        v1, v2 = vals_novel[i], vals_novel[(i + 5) % 16]
        q = k1 if i % 2 else k2
        assert put('HELDOUT_NOVEL_IDS', k1, v1, k2, v2, q)
    # Paired counterfactuals from FIRST 16 TRAIN binding examples, swapping value.
    for original in rows[:16]:
        z = original['context']
        assert put('PAIRED_COUNTERFACTUAL', z[1], z[5], z[4], z[2], z[7], original['id'])
    trial = 0
    while sum(x['group'] == 'HELDOUT_ABSENT' for x in rows) < 8:
        trial += 1
        if trial > 10000:
            stop('NO_UNIQUE_ABSENT')
        k1, k2, kq = rng.sample(keys_seen, 3)
        v1, v2 = rng.sample(vals_seen, 2)
        put('HELDOUT_ABSENT', k1, v1, k2, v2, kq)
    validate_fixture(rows, no_answer)
    return rows


def validate_fixture(rows: list[dict], no_answer: int) -> None:
    by_group = Counter(x['group'] for x in rows)
    if by_group != Counter(GROUPS) or len(rows) != 80:
        stop('FIXTURE_COUNT')
    contexts = [tuple(x['context']) for x in rows]
    if len(set(contexts)) != len(contexts):
        stop('FIXTURE_DUPLICATE')
    bound = 0
    negative = 0
    for r in rows:
        c = r['context']
        if len(c) != 9 or len(r['choices']) != 4 or len(set(r['choices'])) != 4:
            stop('FIXTURE_FORMAT')
        oracle = c[2] if c[7] == c[1] else (c[5] if c[7] == c[4] else no_answer)
        if oracle != r['gold'] or r['gold'] not in r['choices']:
            stop('ORACLE_WRONG')
        if r['group'] == 'TRAIN':
            bound += r['query_position'] in (1, 2)
        # Constant NO_ANSWER and last-value are BOTH deliberately bad.
        negative += (r['gold'] != no_answer) and (r['gold'] != c[5])
    if bound != 16 or negative < 12:
        stop('ANTI_ORACLE_NOT_DISCRIMINATING')
    qp = Counter(r['query_position'] for r in rows if r['group'] == 'TRAIN' and r['query_position'])
    if qp != {1: 8, 2: 8}:
        stop('QUERY_POSITION_BALANCE')
    train_contexts = {tuple(r['context']) for r in rows if r['group'] == 'TRAIN'}
    if any(tuple(r['context']) in train_contexts for r in rows if r['group'] != 'TRAIN'):
        stop('TRAIN_HELDOUT_COLLISION')
    train_token_ids = {z for r in rows if r['group'] == 'TRAIN' for z in r['context']} | {r['gold'] for r in rows if r['group'] == 'TRAIN'}
    if any(r['context'][i] not in train_token_ids for r in rows if r['group'] == 'HELDOUT_RECOMBINED' for i in [1, 2, 4, 5, 7]):
        stop('RECOMBINED_NOT_SEEN_SYMBOLS')
    if any(r['context'][i] in train_token_ids for r in rows if r['group'] == 'HELDOUT_NOVEL_IDS' for i in [1, 2, 4, 5, 7]):
        stop('NOVEL_NOT_NEW_SYMBOLS')
    parents = {r['id']: r for r in rows if r['group'] == 'TRAIN'}
    for r in rows:
        if r['group'] != 'PAIRED_COUNTERFACTUAL':
            continue
        p = parents.get(r['parent'])
        if not p or p['query_position'] not in (1, 2):
            stop('COUNTERFACTUAL_BAD_PARENT')
        a, b = p['context'], r['context']
        if not (a[1] == b[1] and a[4] == b[4] and a[7] == b[7] and
                a[2] == b[5] and a[5] == b[2] and p['gold'] != r['gold']):
            stop('COUNTERFACTUAL_INVALID')


def mock_source_qa() -> dict:
    """No model, checkpoint, or real tokenizer loaded. MOCK inputs only."""
    meta, underlying = mock_token_inventory()
    checks = {}
    ids = permitted_ids(meta, underlying)
    fixture = fixture_generator(ids)
    checks['fixture_80_80_oracle'] = len(fixture) == 80
    checks['fixed_24_56_split'] = sum(r['group'] == 'TRAIN' for r in fixture) == 24
    checks['determinism'] = json_bytes(fixture) == json_bytes(fixture_generator(ids))
    checks['seed_sensitivity'] = json_bytes(fixture) != json_bytes(fixture_generator(ids, seed=SEED + 1))
    checks['no_target_in_input'] = all(r['gold'] != r['context'][-1] for r in fixture)
    checks['train_first_query_balance'] = Counter(r['query_position'] for r in fixture if r['group']=='TRAIN' and r['query_position']) == {1: 8, 2: 8}
    checks['independent_groups'] = Counter(r['group'] for r in fixture) == Counter(GROUPS)
    checks['counterfactual_16'] = sum(r['group']=='PAIRED_COUNTERFACTUAL' for r in fixture)==16
    checks['oracle_not_last_value'] = sum(r['gold'] != r['second_value'] for r in fixture) >= 12
    checks['constant_fails'] = sum(r['gold'] != fixture[0]['gold'] for r in fixture) >= 16
    checks['four_option_distinct'] = all(len(set(r['choices'])) == 4 for r in fixture)
    # Mutations expected to be rejected by the independent validator.
    mock_no_answer = next(r['gold'] for r in fixture if r['group']=='HELDOUT_ABSENT')
    for key,mut in [('tamper_gold',lambda r:r.__setitem__('gold',-1)),
                    ('tamper_context',lambda r:r.__setitem__('context',[1])),
                    ('duplicate_context',lambda r:r.__setitem__('context',fixture[1]['context']))]:
        x = [dict(r) for r in fixture]
        mut(x[0])
        try:
            validate_fixture(x, mock_no_answer)
            checks['reject_'+key] = False
        except RuntimeError:
            checks['reject_'+key] = True
    # Negative controls for forged/unknown token inventories.
    for key,delta in [('forged_sha',{'underlying_inventory_sha256':'a'*64}),
                      ('special_collision',{'reserved_ids':[100]}),
                      ('wrong_vocab',{'vocab_size':4096}),
                      ('invalid_inventory_hash',{'underlying_inventory_sha256':'MOCK'})]:
        mm = dict(meta, **delta)
        try:
            permitted_ids(mm, underlying)
            checks['reject_'+key] = False
        except RuntimeError:
            checks['reject_'+key] = True
    return {'mode':'SOURCE_QA_ONLY','mock':True, 'total':len(checks),
            'passed':sum(bool(v) for v in checks.values()),'checks':checks,
            'fixture_written':False,'model_run':False,'checkpoint_access':False}


def exact_scoped_path(root: Path, path: Path) -> Path:
    """Reject private source paths outside the exact signed project root."""
    from release_auth_v2 import trusted_execution_root
    root = trusted_execution_root(root)
    actual = path.resolve(strict=False)
    if not actual.is_relative_to(root) or actual == root:
        stop('DIRECT_CLI_PATH_ESCAPES_SIGNED_PROJECT')
    return actual


def signed_admission(path: Path, source: Path, meta_path: Path,
                     underlying_path: Path, phase: str,
                     frozen_fixture_sha256: str | None = None,
                     root: Path | None = None) -> dict:
    """Require 3 external cryptographic signatures *before* private byte access.

    The local permit cannot nominate its own public keys. Trust roots are pinned
    in the reviewed release_auth_v2.py code and currently deliberately EMPTY.
    """
    if root is None:
        stop('SIGNED_PROJECT_ROOT_MISSING')
    source = exact_scoped_path(root, source)
    path = exact_scoped_path(root, path)
    meta_path = exact_scoped_path(root, meta_path)
    underlying_path = exact_scoped_path(root, underlying_path)
    guard=source.with_name('release_auth_v2.py')
    if not guard.is_file() or git_blob(guard)!=RELEASE_GUARD_GIT_BLOB:
        stop('RELEASE_GUARD_SOURCE_NOT_PINNED')
    from release_auth_v2 import authenticate_release
    if not source.is_file():
        stop('RUNNER_SOURCE_MISSING')
    if not path.is_file():
        stop('SIGNED_PERMIT_MISSING')
    # Only the permit (untrusted) is read to extract hashes for signature check.
    permit = json_read(path)
    payload = permit.get('payload')
    if not isinstance(payload, dict):
        stop('SIGNED_PERMIT_PAYLOAD_MISSING')
    auth = authenticate_release(
        path, phase=phase, runner_sha256=sha256_file(source),
        tokenizer_sha256=payload.get('token_inventory_sha256'),
        underlying_sha256=payload.get('underlying_inventory_sha256'),
        frozen_fixture_sha256=frozen_fixture_sha256, project_root=root)
    # Safe only after authenticated signatures: private tokenizer source read.
    if not meta_path.is_file() or not underlying_path.is_file():
        stop('TOKENIZER_PRIVATE_SOURCE_MISSING')
    if sha256_file(meta_path) != auth['token_inventory_sha256']:
        stop('TOKEN_META_SIGNATURE_SHA_MISMATCH')
    if sha256_file(underlying_path) != auth['underlying_inventory_sha256']:
        stop('TOKEN_UNDERLYING_SIGNATURE_SHA_MISMATCH')
    return auth


def case_and_group_manifest(rows: list[dict]) -> dict:
    cases = {r['id']: hashlib.sha256(json_bytes(r)).hexdigest() for r in rows}
    groups = {g: hashlib.sha256(json_bytes([r for r in rows if r['group']==g])).hexdigest()
              for g in GROUPS}
    if len(cases)!=80 or any(sum(r['group']==g for r in rows)!=n for g,n in GROUPS.items()):
        stop('CASE_MANIFEST_COUNT')
    return {'case_sha256':cases,'group_sha256':groups,
            'fixture_sha256':hashlib.sha256(json_bytes(rows)).hexdigest(),
            'counts':GROUPS}


def read_frozen_fixture(fixture_dir: Path, signed_fixture_sha: str,
                        meta: dict, underlying: bytes) -> list[dict]:
    """I2 reads the byte-exact 80-case frozen file; never regenerates fixtures."""
    original = fixture_dir/'FIXTURE_RECORDS.json'
    mf_path = fixture_dir/'FIXTURE_MANIFEST.json'
    if not original.is_file() or not mf_path.is_file():
        stop('FROZEN_80_RECORDS_NOT_FOUND')
    if sha256_file(original) != signed_fixture_sha:
        stop('FROZEN_FIXTURE_BYTES_CHANGED')
    try:
        rows = json.loads(original.read_bytes())
    except (ValueError, UnicodeDecodeError):
        stop('FROZEN_FIXTURE_INVALID')
    if not isinstance(rows,list):
        stop('FROZEN_FIXTURE_SCHEMA')
    permitted = permitted_ids(meta, underlying)
    # Reconstructed oracle uses no model outputs and no regenerated fixture.
    ref = fixture_generator(permitted)
    if rows!=ref:
        stop('FROZEN_CASES_NOT_MATCH_PROTOCOL')
    no_answer = next(
        r['gold'] for r in ref if r['group']=='HELDOUT_ABSENT')
    validate_fixture(rows,no_answer)
    manifest = json_read(mf_path)
    if manifest!=case_and_group_manifest(rows):
        stop('FROZEN_CASE_OR_GROUP_MANIFEST_MISMATCH')
    return rows


def fixture_freeze(args):
    """One I1-only future freeze, strictly after external signed rights admission."""
    src = Path(__file__).resolve()
    root = Path(args.root).resolve()
    meta_path = Path(args.token_inventory).resolve()
    underlying_path = Path(args.tokenizer_source).resolve()
    out = Path(args.out).resolve()
    exact_scoped_path(root, out)
    signed_admission(Path(args.permit).resolve(),src,meta_path,underlying_path,
                     phase='fixture-freeze',root=root)
    meta = json_read(meta_path)
    allowed = permitted_ids(meta,underlying_path.read_bytes())
    rows = fixture_generator(allowed)
    mf = case_and_group_manifest(rows)
    if out.exists() or not out.is_relative_to(root) or not out.parent.exists():
        stop('FIXTURE_FREEZE_OUTPUT_LOCATION')
    out.mkdir(exist_ok=False)
    (out/'FIXTURE_RECORDS.json').write_bytes(json_bytes(rows))
    (out/'FIXTURE_MANIFEST.json').write_bytes(json_bytes(mf))
    receipt = dict(schema='ttm.sm4m.diag.q001.I1.fixture_freeze.v2',
                   question_id=QID, source_sha256=sha256_file(src),
                   token_inventory_sha256=sha256_file(meta_path),
                   underlying_inventory_sha256=sha256_file(underlying_path),
                   frozen_fixture_sha256=mf['fixture_sha256'],
                   per_case_manifest_sha256=sha256_file(out/'FIXTURE_MANIFEST.json'),
                   counts=GROUPS, actual_model_access=False, model_run=False,
                   independent_review='NOT_EXECUTED')
    (out/'FIXTURE_FREEZE_RECEIPT.json').write_bytes(json_bytes(receipt))
    print(json.dumps({'status':'FROZEN_I1_NOT_I2_AUTHORIZED',
                      'fixture_sha256':mf['fixture_sha256'],'cases':len(rows)}))

def load_model(checkpoint: Path, root: Path):
    """This function is called ONLY after require_permit and rights admission."""
    import torch
    if torch.__version__ is None or sys.version_info[:2] != (3, 12):
        stop('PYTHON_TORCH_VERSION')
    core = root / 'src' / 'p02' / 'transformer_core.py'
    if git_blob(core) != SOURCE_BLOB:
        stop('P02_GIT_BLOB_MISMATCH')
    if checkpoint.stat().st_size != MODEL_SIZE or sha256_file(checkpoint) != MODEL_SHA:
        stop('CHECKPOINT_HASH_OR_LENGTH')
    spec = importlib.util.spec_from_file_location('p02_reference_locked', core)
    if spec is None or spec.loader is None:
        stop('P02_IMPORT_SPEC')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    cp = torch.load(checkpoint, map_location='cpu', weights_only=True)
    if (cp.get('schema') != 'ttm.t4.science.checkpoint.v1' or
        cp.get('p02_git_blob') != SOURCE_BLOB or cp.get('config') != MODEL_CONFIG or
        cp.get('step') != 1024):
        stop('CHECKPOINT_PAYLOAD_SCHEMA_CONFIG')
    model = module.GPT(module.P02Config(**MODEL_CONFIG))
    if sum(x.numel() for x in model.parameters()) != 3749376:
        stop('PARAMETER_COUNT')
    model.load_state_dict(cp['model'], strict=True)
    model.cpu().float()
    return model,torch


def model_fingerprint(model, torch) -> tuple[str, float]:
    """Exact parameter-byte fingerprint and FP64 L2 norm (not saved weights)."""
    h=hashlib.sha256()
    sq=0.0
    with torch.no_grad():
        for name,p in model.named_parameters():
            t=p.detach().float().cpu().contiguous()
            h.update(name.encode('utf-8')+b'\0')
            h.update(str(tuple(t.shape)).encode('ascii')+b'\0')
            h.update(t.numpy().tobytes(order='C'))
            sq+=float(t.double().square().sum().item())
    return h.hexdigest(),math.sqrt(sq)


def evaluate(model,torch,rows,idxs: list[int],rss_check):
    import torch.nn.functional as F
    model.eval()
    results=[]
    with torch.no_grad():
        for i in idxs:
            rss_check()
            item=rows[i]
            tokens=torch.tensor(item['context'], dtype=torch.long,device='cpu')[None,:]
            logits,_=model(tokens)
            last=logits[0,-1,:].float()
            if not bool(torch.isfinite(last).all()):
                stop('NONFINITE_EVAL_LOGITS')
            target=item['gold']
            prob=F.log_softmax(last,dim=-1)
            full_id=int(last.argmax().item())
            opts=item['choices']
            restricted_id=opts[max(range(4),key=lambda x: float(last[opts[x]].item()))]
            rank=int((last>last[target]).sum().item())+1
            results.append({'id':item['id'],'group':item['group'],'gold':target,
                            'greedy':full_id,'greedy_correct':full_id==target,
                            'candidate_correct':restricted_id==target,
                            'gold_nll':-float(prob[target].item()),
                            'gold_rank':rank,'query_position':item['query_position'],
                            'parent':item['parent']})
    return results


def claim_one_shot(root: Path, nonce: str) -> Path:
    """Persist an atomic no-retry claim before entering the model path.

    Deleting/replacing this file voids local audit custody; external reviewer
    must compare durable GitHub/Windows evidence, not trust local state alone.
    """
    if not isinstance(nonce,str) or len(nonce)!=64 or any(c not in '0123456789abcdef' for c in nonce):
        stop('INVALID_SIGNED_ONESHOT_NONCE')
    from release_auth_v2 import trusted_execution_root
    root = trusted_execution_root(root)
    directory=root/'_evidence'/'ttm_sm4m_diag_q001_onetime_claims'
    legacy=root/'_tmp'/'ttm_sm4m_diag_q001_onetime_claim'/('RUN_'+nonce+'.json')
    if legacy.exists():
        stop('ONESHOT_NONCE_ALREADY_CONSUMED_LEGACY')
    directory.mkdir(parents=True,exist_ok=True)
    if directory.resolve(strict=False) != directory:
        stop('ONESHOT_LEDGER_REPARSE_OR_SYMLINK')
    target=directory/('RUN_'+nonce+'.json')
    try:
        fd=os.open(str(target),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError:
        stop('ONESHOT_NONCE_ALREADY_CONSUMED_NO_RETRY')
    try:
        with os.fdopen(fd,'wb') as out:
            out.write(json_bytes({'one_shot_nonce':nonce,'status':'CLAIMED_NO_RETRY',
                                  'question_id':QID,'checkpoint_sha256':MODEL_SHA}))
            out.flush()
            os.fsync(out.fileno())
    except BaseException:
        # Fail closed: never clear the claim on failure; no automatic retry.
        raise
    return target


def run(args):
    src=Path(__file__).resolve()
    root=Path(args.root).resolve()
    checkpoint=Path(args.checkpoint).resolve()
    inventory=Path(args.token_inventory).resolve()
    underlying=Path(args.tokenizer_source).resolve()
    fixture_dir=Path(args.fixture_dir).resolve()
    permit_path=Path(args.permit).resolve()
    for check_path in (src,checkpoint,inventory,underlying,fixture_dir,permit_path,Path(args.out)):
        exact_scoped_path(root,check_path)
    # Extract untrusted claimed fixture digest for cryptographic validation;
    # do NOT read private inventory or checkpoint before authenticated release.
    packet=json_read(permit_path)
    payload=packet.get('payload')
    if not isinstance(payload,dict):
        stop('SIGNED_RUN_PAYLOAD_MISSING')
    fixture_digest=payload.get('frozen_fixture_sha256')
    signed_admission(permit_path,src,inventory,underlying,'run',fixture_digest,root=root)
    if not checkpoint.is_file() or checkpoint.stat().st_size!=MODEL_SIZE or sha256_file(checkpoint)!=MODEL_SHA:
        stop('CHECKPOINT_PRIVATE_BYTES_MISMATCH')
    import psutil
    process=psutil.Process(os.getpid())
    begin=time.monotonic()
    peak_rss=0
    def resource_guard():
        nonlocal peak_rss
        peak_rss=max(peak_rss,process.memory_info().rss)
        if time.monotonic()-begin>WALL_SECONDS:
            stop('RESOURCE_WALL_TIME_900S')
        if peak_rss>MEMORY_BYTES:
            stop('RESOURCE_RSS_12GIB')
    meta=json_read(inventory)
    rows=read_frozen_fixture(fixture_dir,fixture_digest,meta,underlying.read_bytes())
    claim_file=claim_one_shot(root,payload.get('one_shot_nonce'))
    model,torch=load_model(checkpoint,root)
    torch.set_num_threads(min(8,max(1,os.cpu_count() or 1)))
    torch.manual_seed(SEED)
    fixture_hash=hashlib.sha256(json_bytes(rows)).hexdigest()
    # Model execution begins only after signed release, custody and fixture checks.
    all_idx=list(range(len(rows)))
    baseline=evaluate(model,torch,rows,all_idx,resource_guard)
    # Finite nonzero post-update weight delta is an explicit primary validity gate.
    before=[p.detach().clone() for p in model.parameters()]
    param_sha_before,param_norm_before=model_fingerprint(model,torch)
    opt=torch.optim.AdamW(model.parameters(),lr=0.001,betas=(0.9,0.95),eps=1e-8,weight_decay=0)
    train_idx=[i for i,r in enumerate(rows) if r['group']=='TRAIN']
    rng=random.Random(SEED)
    epoch=[]
    monitor=[]
    for step in range(1,MAX_STEPS+1):
        resource_guard()
        if not epoch:
            epoch=train_idx[:]
            rng.shuffle(epoch)
        b=[epoch.pop() for _ in range(8)]
        x=torch.tensor([rows[i]['context'] for i in b],dtype=torch.long)
        y=torch.tensor([rows[i]['gold'] for i in b],dtype=torch.long)
        model.train()
        opt.zero_grad(set_to_none=True)
        logits,_=model(x)
        # Exactly ninth-context position -> tenth token. NOT full prompt CE.
        answer_logits=logits[:,-1,:].float()
        loss=torch.nn.functional.cross_entropy(answer_logits,y)
        if not bool(torch.isfinite(loss)):
            stop('NONFINITE_LOSS')
        loss.backward()
        norms=[p.grad.detach().float().norm() for p in model.parameters() if p.grad is not None]
        if not norms or not all(bool(torch.isfinite(z)) for z in norms):
            stop('NONFINITE_OR_MISSING_GRAD')
        torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
        opt.step()
        if step in (32,64,128,256):
            monitor.append({'step':step,'train_batch_loss':float(loss.item()),
                            'grad_sum_norm':sum(float(n.item()) for n in norms),
                            'elapsed':time.monotonic()-begin})
    with torch.no_grad():
        abs_delta=float(sum((p.detach()-before[i]).abs().sum().item()
                            for i,p in enumerate(model.parameters())))
    if not math.isfinite(abs_delta) or abs_delta<=0:
        stop('ZERO_OR_NONFINITE_WEIGHT_DELTA')
    param_sha_after,param_norm_after=model_fingerprint(model,torch)
    if param_sha_after==param_sha_before:
        stop('PARAMETER_FINGERPRINT_UNCHANGED')
    post=evaluate(model,torch,rows,all_idx,resource_guard)
    post_by=Counter()
    for r in post:
        post_by[r['group']]+=int(r['greedy_correct'])
    train=[r for r in post if r['group']=='TRAIN']
    train_nll=sum(r['gold_nll'] for r in train)/24
    achieved=post_by['TRAIN']==24 and train_nll<=.10
    receipt={
      'schema':'ttm.sm4m.diag.q001.single_run_receipt.v2','question_id':QID,
      'status':'COMPLETED_ONE_SHOT_TINY_OVERFIT_PASS' if achieved else 'COMPLETED_ONE_SHOT_TINY_OVERFIT_NOT_REACHED',
      'scope':'SYNTHETIC_ONLY_NO_SEMANTIC_BENCHMARK_CLAIM','seed':SEED,'steps':256,
      'model_sha256':MODEL_SHA,'p02_blob':SOURCE_BLOB,'fixture_sha256':fixture_hash,
      'one_shot_nonce':payload['one_shot_nonce'],'claim_file':str(claim_file),
      'runner_sha256':sha256_file(src),'groups':GROUPS,
      'post_correct_by_group':dict(post_by),'train_ce':train_nll,'monitor':monitor,
      'baseline':baseline,'post':post,'resource_elapsed_s':time.monotonic()-begin,
      'peak_rss_bytes_sampled':peak_rss,'parameter_absolute_delta_sum':abs_delta,
      'parameter_sha256_before':param_sha_before,'parameter_sha256_after':param_sha_after,
      'parameter_L2_norm_before':param_norm_before,'parameter_L2_norm_after':param_norm_after,
      'python_version':sys.version,'torch_version':torch.__version__,
      'limited_four_way_candidate_semantics':'GOLD_AT_INDEX_ZERO; SORTED_LOW_VALUE_DISTRACTORS; RESTRICTED_RESULT_EXPLORATORY_ONLY',
      'independent_adjudication':'PENDING','historical_TEST_FINAL_replayed':False,
      'fine_tuned_weights_persisted':False}
    raw=json_bytes(receipt)
    if len(raw)>OUTPUT_BYTES:
        stop('OUTPUT_SIZE_CAP')
    out=Path(args.out).resolve()
    if out.exists() or not out.is_relative_to(root):
        stop('OUTPUT_MUST_BE_NEW_AND_INSIDE_PROJECT')
    out.mkdir(parents=True,exist_ok=False)
    (out/'RUN_RECEIPT.json').write_bytes(raw)
    (out/'RUN_RECEIPT.sha256').write_text(hashlib.sha256(raw).hexdigest()+'\n',encoding='ascii')
    print(json.dumps({'status':receipt['status'],'report':str(out/'RUN_RECEIPT.json'),
                      'sha256':hashlib.sha256(raw).hexdigest(),
                      'steps':256,'train_correct':post_by['TRAIN'],'weight_delta':abs_delta,
                      'train_CE':train_nll,'other_correct':dict(post_by)},sort_keys=True))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode',choices=['source-qa','release-preflight','fixture-freeze','run'])
    ap.add_argument('--root',default='')
    ap.add_argument('--permit',default='')
    ap.add_argument('--checkpoint',default='')
    ap.add_argument('--token-inventory',default='')
    ap.add_argument('--tokenizer-source',default='')
    ap.add_argument('--fixture-dir',default='')
    ap.add_argument('--out',default='')
    args=ap.parse_args()
    try:
        if args.mode=='source-qa':
            out=mock_source_qa()
            print(json.dumps(out,sort_keys=True))
            if out['passed'] != out['total']:
                sys.exit(3)
        elif args.mode=='release-preflight':
            if not all([args.root,args.permit,args.token_inventory,args.tokenizer_source,args.fixture_dir]):
                stop('MISSING_RELEASE_PREFLIGHT_ARGUMENTS')
            root=Path(args.root).resolve()
            for check_path in (Path(__file__).resolve(),Path(args.permit),
                               Path(args.token_inventory),Path(args.tokenizer_source),
                               Path(args.fixture_dir)):
                exact_scoped_path(root,check_path)
            packet=json_read(Path(args.permit).resolve())
            payload=packet.get('payload')
            if not isinstance(payload,dict) or not isinstance(payload.get('frozen_fixture_sha256'),str):
                stop('SIGNED_PREFLIGHT_PAYLOAD_REQUIRED')
            signed_admission(Path(args.permit).resolve(), Path(__file__).resolve(),
                             Path(args.token_inventory).resolve(),
                             Path(args.tokenizer_source).resolve(),'run',
                             payload['frozen_fixture_sha256'],root=root)
            print(json.dumps({'status':'SIGNED_RELEASE_PREFLIGHT_PASS_NO_CHECKPOINT_READ'}))
        elif args.mode=='fixture-freeze':
            if not all([args.root,args.permit,args.token_inventory,args.tokenizer_source,args.out]):
                stop('MISSING_FIXTURE_FREEZE_ARGUMENTS')
            fixture_freeze(args)
        else:
            if not all([args.root,args.permit,args.checkpoint,args.token_inventory,args.tokenizer_source,args.fixture_dir,args.out]):
                stop('MISSING_REQUIRED_RUN_FLAGS')
            run(args)
    except Exception as exc:
        print(json.dumps({'status':'HOLD','error':str(exc),'run_finished':False,
                          'model_execution_not_asserted':True},sort_keys=True),file=sys.stderr)
        sys.exit(2)

if __name__=='__main__':
    main()
