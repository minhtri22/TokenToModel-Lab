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

# Python -I omits the script directory. Resolve reviewed companions here.
sys.path.insert(0, str(Path(__file__).resolve().parent))

QID = 'TTM-SM4M-DIAG-Q001'
SOURCE_BLOB = '9762343e06cf800b50574c2871ae1ed58537fb18'
MODEL_SHA = 'cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b'
RELEASE_GUARD_GIT_BLOB = '273cc989d5e94ae7a8e58c08a709cf7dd8229ab2'
RSS_MODULE_GIT_BLOB = '51748fb86184ec8dd9de51211b3173514255c159'
OWNER_INTERNAL_GUARD_GIT_BLOB = 'd816fd282f717669cd127732f49254d5b6e604a5'
JOB_MODULE_GIT_BLOB = '3060e77fceb8dc76c8f96996281fd2034a6082bc'
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
    ids = list(range(300, 500))
    reserved = list(range(300)) + list(range(500, 2048))
    inv = dict(schema='ttm.sm4m.diag.tokenizer_full_inventory.v1',
               vocab_size=2048, non_special_token_ids=ids,
               special_ids=[], reserved_ids=reserved)
    raw = json_bytes(inv)
    meta = dict(schema='ttm.sm4m.diag.tokenizer_allowed_ids.v1',
                vocab_size=2048, allowed_non_special_ids=ids,
                reserved_ids=reserved, underlying_inventory_sha256=hashlib.sha256(raw).hexdigest())
    return meta, raw

# Track A source custody: exact Git LF bytes OR their deterministic CRLF checkout.
# Hash the very same buffer that compile() executes; never ask importlib to run .pyc.
TRACK_A_V3_SOURCE_SHA256 = '2d0b980768a0ac3079f361d94244cd694c97ed90e978fc83fb7991dc82b5c2ac'
TRACK_A_V3_CRLF_SHA256 = 'd76936db04caec358ddfb6947656d60023dee7de5c3388f810c7ecbf08288b63'
TRACK_A_V3_PRE_REPAIR_SCORER_SHA256 = '98101e871410e7255cd25f611e5eb9d7068ab264ac162e0af89ef1f1863f6587'
TRACK_A_V3_FROZEN_RECORDS_SHA256 = '823a08dd4be0da7748cb258b9bf5b2841dd1fdbac84956eb204be7ba57f8c55d'
TRACK_A_V3_FROZEN_MANIFEST_SHA256 = '0b80368a6747994df5f5b8d0e7b35137266ac82f6c9b83d26af5b61f79b3cb04'
TRACK_A_V3_PROTOCOL = 'ttm.sm4m.q001.track_a.measurement.v3.integrated'


def track_a_v3():
    """Compile only the SHA-verified source buffer, bypassing .pyc and TOCTOU."""
    import types

    source = (Path(__file__).resolve().parent.parent /
              'track_a_m0_v3' / 'q001_m0_goldblind.py')
    if not source.is_file():
        stop('TRACK_A_V3_SOURCE_MISSING')
    raw = source.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual not in (TRACK_A_V3_SOURCE_SHA256, TRACK_A_V3_CRLF_SHA256):
        stop('TRACK_A_V3_SOURCE_SHA_MISMATCH')
    # Mixed EOL, lone CR and rewritten bytes are disallowed, not normalized away.
    if b'\r\n' in raw:
        if b'\n' in raw.replace(b'\r\n', b'') or b'\r' in raw.replace(b'\r\n', b''):
            stop('TRACK_A_V3_MIXED_EOL')
        canonical = raw.replace(b'\r\n', b'\n')
    else:
        if b'\r' in raw:
            stop('TRACK_A_V3_MIXED_EOL')
        canonical = raw
    if hashlib.sha256(canonical).hexdigest() != TRACK_A_V3_SOURCE_SHA256:
        stop('TRACK_A_V3_CANONICAL_SHA_MISMATCH')
    try:
        code = compile(canonical.decode('utf-8'), str(source), 'exec',
                       dont_inherit=True)
    except (UnicodeError, SyntaxError) as exc:
        stop('TRACK_A_V3_VERIFIED_COMPILE_FAILED')
    module = types.ModuleType('_ttm_sm4m_track_a_v3')
    module.__file__ = str(source)
    exec(code, module.__dict__)
    return module

def fixture_generator(allowed: list[int], seed: int = SEED) -> list[dict]:
    """Versioned gold-blind fixture; older frozen record bytes are invalid."""
    return track_a_v3().make_fixture(allowed, seed)


def validate_fixture(rows: list[dict], no_answer: int) -> None:
    try:
        track_a_v3().validate_fixture(rows)
        if any(r['no_answer'] != no_answer for r in rows):
            stop('V3_NO_ANSWER_ROLE_MISMATCH')
    except ValueError as exc:
        stop('V3_FIXTURE_VALIDATION_' + str(exc))

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
    checks['train_first_query_balance'] = Counter((1 if r['context'][7] == r['context'][1] else 2) for r in fixture if r['group']=='TRAIN' and r['gold'] != r['no_answer']) == {1: 8, 2: 8}
    checks['independent_groups'] = Counter(r['group'] for r in fixture) == Counter(GROUPS)
    checks['counterfactual_16'] = sum(r['group']=='PAIRED_COUNTERFACTUAL' for r in fixture)==16
    checks['oracle_not_last_value'] = sum(r['gold'] != r['context'][5] for r in fixture) >= 12
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
        except (RuntimeError, ValueError):
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
        except (RuntimeError, ValueError):
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
    if permit.get('mode') is not None:
        stop('LOCAL_OWNER_PACKET_DENIED')
    auth=authenticate_release(
        path, phase=phase, runner_sha256=sha256_file(source),
        tokenizer_sha256=payload.get('token_inventory_sha256'),
        underlying_sha256=payload.get('underlying_inventory_sha256'),
        frozen_fixture_sha256=frozen_fixture_sha256, project_root=root)
    # Allowed only after one exact approved admission mode; now validate bytes.
    if not meta_path.is_file() or not underlying_path.is_file():
        stop('TOKENIZER_PRIVATE_SOURCE_MISSING')
    if sha256_file(meta_path) != auth['token_inventory_sha256']:
        stop('TOKEN_META_SIGNATURE_SHA_MISMATCH')
    if sha256_file(underlying_path) != auth['underlying_inventory_sha256']:
        stop('TOKEN_UNDERLYING_SIGNATURE_SHA_MISMATCH')
    return auth


def owner_admission(args, root: Path, *, run: bool):
    if args.permit or args.token_inventory:
        stop('LOCAL_OWNER_PACKET_DENIED')
    src = Path(__file__).resolve()
    exact_scoped_path(root, src)
    module = src.with_name('owner_internal_admission.py')
    if not module.is_file() or git_blob(module) != OWNER_INTERNAL_GUARD_GIT_BLOB:
        stop('OWNER_INTERNAL_ADMISSION_SOURCE_NOT_PINNED')
    from owner_internal_admission import (
        ONE_SHOT_NONCE, original_token_ids, published_fixture_sha256, require_scope,
    )
    require_scope(root)
    digest = published_fixture_sha256(root) if run else None
    tokenizer = exact_scoped_path(root, Path(args.tokenizer_source))
    return original_token_ids(tokenizer.read_bytes()), digest, ONE_SHOT_NONCE


def require_hard_job():
    job = Path(__file__).resolve().with_name('windows_job_memory_limit.py')
    if not job.is_file() or git_blob(job) != JOB_MODULE_GIT_BLOB:
        stop('WINDOWS_JOB_OBJECT_MODULE_NOT_PINNED')
    from windows_job_memory_limit import require_current_job
    require_current_job()


def case_and_group_manifest(rows: list[dict]) -> dict:
    cases = {r['id']: hashlib.sha256(json_bytes(r)).hexdigest() for r in rows}
    groups = {g: hashlib.sha256(json_bytes([r for r in rows if r['group']==g])).hexdigest()
              for g in GROUPS}
    if len(cases)!=80 or any(sum(r['group']==g for r in rows)!=n for g,n in GROUPS.items()):
        stop('CASE_MANIFEST_COUNT')
    return {'protocol_schema':TRACK_A_V3_PROTOCOL,
            'scorer_sha256':TRACK_A_V3_SOURCE_SHA256,
            'case_sha256':cases,'group_sha256':groups,
            'fixture_sha256':hashlib.sha256(json_bytes(rows)).hexdigest(),
            'counts':GROUPS}


def read_frozen_fixture(fixture_dir: Path, signed_fixture_sha: str,
                        meta: dict | None = None, underlying: bytes | None = None,
                        *, allowed: list[int] | None = None) -> list[dict]:
    """I2 reads the byte-exact 80-case frozen file; never regenerates fixtures."""
    original = fixture_dir/'FIXTURE_RECORDS.json'
    mf_path = fixture_dir/'FIXTURE_MANIFEST.json'
    if original.resolve() != original.absolute():
        stop('FROZEN_FIXTURE_RECORDS_REPARSE')
    if mf_path.resolve() != mf_path.absolute():
        stop('FROZEN_FIXTURE_MANIFEST_REPARSE')
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
    permitted = allowed if allowed is not None else permitted_ids(meta, underlying)
    # Check the frozen bytes against the deterministic oracle in memory.
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
    """Freeze the 80 cases before I2, within the admitted I1 scope."""
    src = Path(__file__).resolve()
    root = Path(args.root).resolve()
    meta_path = Path(args.token_inventory).resolve()
    underlying_path = Path(args.tokenizer_source).resolve()
    out = Path(args.out).resolve()
    exact_scoped_path(root, out)
    if args.owner_internal:
        allowed, _, _ = owner_admission(args, root, run=False)
    else:
        signed_admission(Path(args.permit).resolve(),src,meta_path,underlying_path,
                         phase='fixture-freeze',root=root)
        allowed = permitted_ids(json_read(meta_path), underlying_path.read_bytes())
    rows = fixture_generator(allowed)
    mf = case_and_group_manifest(rows)
    if out.exists() or not out.is_relative_to(root) or not out.parent.exists():
        stop('FIXTURE_FREEZE_OUTPUT_LOCATION')
    out.mkdir(exist_ok=False)
    (out/'FIXTURE_RECORDS.json').write_bytes(json_bytes(rows))
    (out/'FIXTURE_MANIFEST.json').write_bytes(json_bytes(mf))
    receipt = dict(schema='ttm.sm4m.diag.q001.I1.fixture_freeze.v3',
                    protocol_schema=TRACK_A_V3_PROTOCOL,
                    scorer_sha256=TRACK_A_V3_SOURCE_SHA256,
                   question_id=QID, source_sha256=sha256_file(src),
                   token_inventory_sha256=None if args.owner_internal else sha256_file(meta_path),
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
    if torch.__version__ != "2.11.0+cpu" or sys.version_info[:2] != (3, 12):
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


def evaluate_goldblind_logits(logits: list[float], item: dict) -> dict:
    """Source-only and guarded real runner use exactly the same v3 scorer."""
    m = track_a_v3().score_logits(logits, item)
    return {'gold_nll':m['full_vocab_gold_nll'],
            'gold_rank':m['full_vocab_gold_rank'],
            'greedy_correct':m['full_vocab_top1_correct'],
            'candidate_correct':m['candidate_only_top1_correct_secondary'],
            'candidate_tie_abstained':m['candidate_tie_abstained'],
            'full_vocab_tie_abstained':m['full_vocab_tie_abstained'],
            'context_contrast_logit_margin':m['context_contrast_logit_margin']}


def evaluate(model,torch,rows,idxs: list[int],rss_check):
    model.eval()
    results=[]
    with torch.no_grad():
        for i in idxs:
            rss_check()
            item=rows[i]
            tokens=torch.tensor(item['context'],dtype=torch.long,device='cpu')[None,:]
            logits,_=model(tokens)
            last=logits[0,-1,:].float()
            if not bool(torch.isfinite(last).all()):
                stop('NONFINITE_EVAL_LOGITS')
            values=last.tolist()
            m=evaluate_goldblind_logits(values,item)
            maximum=max(values)
            winners=[j for j,x in enumerate(values) if x==maximum]
            greedy=winners[0] if len(winners)==1 else None
            ctx=item['context']
            query_pos=1 if ctx[7]==ctx[1] else 2 if ctx[7]==ctx[4] else 0
            results.append({'id':item['id'],'group':item['group'],
                            'gold':item['gold'],'greedy':greedy,
                            'query_position':query_pos,'parent':item['parent'],**m})
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
    if directory.resolve(strict=False) != directory:
        stop('ONESHOT_LEDGER_REPARSE_OR_SYMLINK')
    directory.mkdir(parents=True,exist_ok=True)
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
    fixture_dir=Path(args.fixture_dir).resolve()
    require_hard_job()
    for check_path in (src, checkpoint, fixture_dir, Path(args.out)):
        exact_scoped_path(root, check_path)
    if args.owner_internal:
        allowed, fixture_digest, nonce = owner_admission(args, root, run=True)
        rows = read_frozen_fixture(fixture_dir, fixture_digest, allowed=allowed)
    else:
        inventory = exact_scoped_path(root, Path(args.token_inventory))
        underlying = exact_scoped_path(root, Path(args.tokenizer_source))
        permit_path = exact_scoped_path(root, Path(args.permit))
        payload = json_read(permit_path).get('payload')
        if not isinstance(payload, dict):
            stop('SIGNED_RUN_PAYLOAD_MISSING')
        fixture_digest = payload.get('frozen_fixture_sha256')
        admission = signed_admission(permit_path, src, inventory, underlying,
                                     'run', fixture_digest, root=root)
        nonce = admission['one_shot_nonce']
        rows = read_frozen_fixture(fixture_dir, fixture_digest,
                                   json_read(inventory), underlying.read_bytes())
    if not checkpoint.is_file() or checkpoint.stat().st_size!=MODEL_SIZE or sha256_file(checkpoint)!=MODEL_SHA:
        stop('CHECKPOINT_PRIVATE_BYTES_MISMATCH')
    # Stdlib Windows RSS replaces optional psutil, with Git blob custody.
    rss_module = src.with_name('windows_rss_native.py')
    if not rss_module.is_file() or git_blob(rss_module) != RSS_MODULE_GIT_BLOB:
        stop('WINDOWS_RSS_NATIVE_MODULE_NOT_PINNED')
    from windows_rss_native import current_process_rss_bytes
    begin=time.monotonic()
    peak_rss=0
    def resource_guard():
        nonlocal peak_rss
        peak_rss=max(peak_rss,current_process_rss_bytes())
        if time.monotonic()-begin>WALL_SECONDS:
            stop('RESOURCE_WALL_TIME_900S')
        if peak_rss>MEMORY_BYTES:
            stop('RESOURCE_RSS_12GIB')
    claim_file=claim_one_shot(root,nonce)
    model,torch=load_model(checkpoint,root)
    torch.set_num_threads(min(8,max(1,os.cpu_count() or 1)))
    torch.manual_seed(SEED)
    fixture_hash=hashlib.sha256(json_bytes(rows)).hexdigest()
    # Model execution begins only after release, custody and fixture checks.
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
      'one_shot_nonce':nonce,'claim_file':claim_file.name,
      'runner_sha256':sha256_file(src),'groups':GROUPS,
      'post_correct_by_group':dict(post_by),'train_ce':train_nll,'monitor':monitor,
      'baseline':baseline,'post':post,'resource_elapsed_s':time.monotonic()-begin,
      'peak_rss_bytes_sampled':peak_rss,'parameter_absolute_delta_sum':abs_delta,
      'parameter_sha256_before':param_sha_before,'parameter_sha256_after':param_sha_after,
      'parameter_L2_norm_before':param_norm_before,'parameter_L2_norm_after':param_norm_after,
      'python_version':sys.version,'torch_version':torch.__version__,
      'limited_four_way_candidate_semantics':'GOLD_BLIND_VISIBLE_CONTEXT_CANDIDATES; TIES_ABSTAIN; SECONDARY_ONLY',
       'measurement_protocol':TRACK_A_V3_PROTOCOL,
       'measurement_scorer_sha256':TRACK_A_V3_SOURCE_SHA256,
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
    ap.add_argument('--owner-internal', action='store_true')
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
            return
        if not args.owner_internal and not (args.permit and args.token_inventory):
            stop('MISSING_LEGACY_ADMISSION_FLAGS')
        if not args.root or not args.tokenizer_source:
            stop('MISSING_SCOPED_SOURCE_FLAGS')
        if args.mode == 'fixture-freeze':
            if not args.out:
                stop('MISSING_FIXTURE_FREEZE_OUTPUT')
            fixture_freeze(args)
        elif args.mode == 'release-preflight':
            if not args.fixture_dir:
                stop('MISSING_FROZEN_FIXTURE_DIR')
            root = Path(args.root).resolve()
            source = Path(__file__).resolve()
            fixture = exact_scoped_path(root, Path(args.fixture_dir))
            if args.owner_internal:
                allowed, digest, _ = owner_admission(args, root, run=True)
                read_frozen_fixture(fixture, digest, allowed=allowed)
            else:
                permit = exact_scoped_path(root, Path(args.permit))
                payload = json_read(permit).get('payload')
                if not isinstance(payload, dict) or not isinstance(payload.get('frozen_fixture_sha256'), str):
                    stop('SIGNED_PREFLIGHT_PAYLOAD_REQUIRED')
                signed_admission(permit, source, Path(args.token_inventory).resolve(),
                                 Path(args.tokenizer_source).resolve(), 'run',
                                 payload['frozen_fixture_sha256'], root=root)
            print(json.dumps({'status':'RELEASE_PREFLIGHT_PASS_NO_CHECKPOINT_READ'}))
        else:
            if not all((args.checkpoint, args.fixture_dir, args.out)):
                stop('MISSING_REQUIRED_RUN_FLAGS')
            run(args)
    except Exception as exc:
        message = str(exc).casefold()
        resource = (isinstance(exc, MemoryError)
                    or getattr(exc, 'winerror', None) in (8, 14, 112, 1455, 1816)
                    or any(marker in message for marker in (
                        'hold_resource_', 'hold_winjob_', 'hold_output_size_cap',
                        "can't allocate memory", 'not enough memory', 'out of memory',
                        'paging file is too small', 'not enough quota')))
        print(json.dumps({'status':'HOLD_RESOURCE_INCOMPLETE' if resource else 'HOLD',
                          'error':str(exc), 'run_finished':False}, sort_keys=True),
              file=sys.stderr)
        sys.exit(86 if resource else 2)

if __name__=='__main__':
    main()
