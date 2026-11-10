#!/usr/bin/env python3
"""TTM original T4: verified 1024->1280 checkpoint continuation (new science lock required).

Source artifact; never runs training on import. Parent T4 files and TEST are immutable.
Cross-research modules and inference runners are never imported. --mode inspect is CPU/read-only.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import random
import sys
import time
import numpy as np
import torch

RUN_ID = 'ttm_small4m_step1024_to1280_exploratory_v1'
PARENT_RUN = 't4_science_4m_1024_a2_20261108_v1'
START, END, MID, TARGETS = 1024, 1280, 1152, 4096
PARENT_SHA = 'cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b'
PARENT_PROGRESS_SHA = '5517cc691fc803eaa69db4078f1f3b3ed78f99fa3c012cb17fd8655123c606ec'
OLD_LOCK_SHA = 'fd183ade2a696d40313aae19b63429d4ef3edd8abf25c899c8cc496836d36817'
PACK_SHA = '184f68b4c0c800ef3e98362c2e20e1cd35baa269e926489a475664526ecd9913'
MANIFEST_SHA = 'ef2e6e67d49b1d5a921b1051df329f15574f1c10cece0ce49468acb53322d650'
PINNED_GIT_BLOBS = {
    'p02': '9762343e06cf800b50574c2871ae1ed58537fb18',
    'trainer': '76c4d0155cd0736919f41682f240b47ad3d7c428',
    'capacity': 'c9a6f256ba975228683ee7de2a1090e649110e97',
    'evaluator': 'bef006bdff173fba6d8ba4aa0ef687a1732fd7c4',
}
EXPECTED_CONFIG = dict(vocab_size=2048, max_seq_len=256, n_embd=256,
                       n_layer=4, n_head=4, norm_type='layernorm')


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise RuntimeError(marker)


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda: f.read(1 << 20), b''):
            h.update(part)
    return h.hexdigest()


def git_blob(path: Path) -> str:
    b = Path(path).read_bytes()
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def json_read(path: Path) -> dict:
    result = json.loads(Path(path).read_text(encoding='utf-8'))
    require(isinstance(result, dict), 'JSON_OBJECT_REQUIRED')
    return result


def json_new(path: Path, obj: dict) -> None:
    with Path(path).open('x', encoding='utf-8') as f:
        json.dump(obj, f, sort_keys=True, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def checked_paths(paths: dict[str, Path]) -> None:
    for name, path in paths.items():
        p = Path(path)
        require(p.is_file() and not p.is_symlink(), 'SOURCE_NOT_REGULAR:' + name)
        require(git_blob(p) == PINNED_GIT_BLOBS[name], 'SOURCE_GIT_BLOB_MISMATCH:' + name)


def checked_parent(folder: Path, *, load_payload: bool = True):
    """Verify immutable original READY/progress/checkpoint without creating output."""
    folder = Path(folder)
    require(folder.name == 'step_1024', 'NOT_ORIGINAL_STEP1024_DIR')
    ready_path, ckpt, prog = [folder / name for name in
                              ('READY.json', 'checkpoint.pt', 'progress.json')]
    for p in (ready_path, ckpt, prog):
        require(p.is_file() and not p.is_symlink(), 'PARENT_FILE_MISSING_OR_LINK:' + p.name)
    ready = json_read(ready_path)
    require(ready.get('schema') == 'ttm.t4.ready.last.v1' and ready.get('step') == START,
            'PARENT_READY_SCHEMA_OR_STEP')
    require(ready.get('checkpoint') == 'checkpoint.pt', 'PARENT_READY_PATH_INVALID')
    require(ready.get('sha256') == PARENT_SHA and sha_file(ckpt) == PARENT_SHA,
            'PARENT_CHECKPOINT_SHA_MISMATCH')
    require(ready.get('bytes') == ckpt.stat().st_size, 'PARENT_CHECKPOINT_BYTES_MISMATCH')
    require(ready.get('science_lock_sha256') == OLD_LOCK_SHA,
            'PARENT_SCIENCE_LOCK_MISMATCH')
    require(ready.get('train_pack_sha256') == PACK_SHA,
            'PARENT_PACK_SHA_MISMATCH')
    require(ready.get('progress_sha256') == PARENT_PROGRESS_SHA and
            sha_file(prog) == PARENT_PROGRESS_SHA, 'PARENT_PROGRESS_SHA_MISMATCH')
    progress = json_read(prog)
    require(progress.get('schema') == 'ttm.t4.progress.v1' and progress.get('step') == START,
            'PARENT_PROGRESS_SCHEMA')
    logs = progress.get('records')
    require(isinstance(logs, list) and len(logs) == START and
            all(e.get('step') == i + 1 and e.get('exact_scored_targets') == TARGETS
                for i, e in enumerate(logs)), 'PARENT_PROGRESS_STEP_PREFIX_INVALID')
    if not load_payload:
        return ready, logs, None
    payload = torch.load(ckpt, map_location='cpu', weights_only=True)
    require(isinstance(payload, dict) and payload.get('schema') == 'ttm.t4.science.checkpoint.v1',
            'PARENT_PAYLOAD_SCHEMA')
    require(payload.get('step') == START and payload.get('science_seed') == 20261108,
            'PARENT_PAYLOAD_STEP_SEED')
    require(payload.get('science_lock_sha256') == OLD_LOCK_SHA and
            payload.get('train_pack_sha256') == PACK_SHA, 'PARENT_PAYLOAD_SOURCE')
    require(payload.get('p02_git_blob') == PINNED_GIT_BLOBS['p02'] and
            payload.get('config') == EXPECTED_CONFIG, 'PARENT_MODEL_ARCH')
    require(payload.get('device_type') == 'cuda' and payload.get('grad_scaler_state') is not None,
            'PARENT_FP16_CUDA_SCALER_MISSING')
    for field in ('model', 'optimizer', 'scheduler', 'sampler_state', 'torch_cpu_rng',
                  'torch_cuda_rng', 'python_rng', 'numpy_rng', 'grad_scaler_state'):
        require(field in payload and payload[field] is not None, 'PARENT_MISSING_STATE:' + field)
    assert_adamw_at_step(payload['optimizer'], START)
    assert_schedule_at_step(payload['scheduler'], payload['optimizer'], START)
    return ready, logs, payload


def assert_adamw_at_step(state: dict, step: int) -> None:
    require(isinstance(state, dict) and isinstance(state.get('param_groups'), list) and
            len(state['param_groups']) == 1, 'ADAMW_GROUPS_MISMATCH')
    group = state['param_groups'][0]
    require(tuple(group.get('betas', ())) == (.9, .95) and
            math.isclose(group.get('weight_decay', -1), .1) and
            math.isclose(group.get('eps', -1), 1e-8), 'ADAMW_HYPERPARAMS_MISMATCH')
    require(math.isclose(float(group.get('lr', -1)), 3e-5, rel_tol=1e-6, abs_tol=1e-10),
            'ADAMW_LR_NOT_ORIGINAL_FLOOR')
    states = state.get('state')
    require(isinstance(states, dict) and len(states) == len(group['params']) > 0,
            'ADAMW_STATE_MISSING_FOR_PARAMETER')
    for item in states.values():
        n = item.get('step', -1)
        require(float(n) == step and 'exp_avg' in item and 'exp_avg_sq' in item,
                'ADAMW_STEP_OR_MOMENTS_MISSING')


def assert_schedule_at_step(sch: dict, opt: dict, step: int) -> None:
    require(isinstance(sch, dict) and sch.get('last_epoch') == step,
            'LAMBDA_SCHEDULER_STEP_MISMATCH')
    require(sch.get('base_lrs') == [3e-4], 'LAMBDA_SCHEDULER_BASE_LR_MISMATCH')
    require(len(sch.get('_last_lr', [])) == 1 and
            math.isclose(sch['_last_lr'][0], opt['param_groups'][0]['lr'], rel_tol=1e-8),
            'LAMBDA_SCHEDULER_LAST_LR_MISMATCH')


def assert_same(a, b, label: str) -> None:
    if isinstance(a, torch.Tensor) and isinstance(b, torch.Tensor):
        require(a.shape == b.shape and a.dtype == b.dtype and
                torch.equal(a.detach().cpu(), b.detach().cpu()), label)
    elif isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
        require(np.array_equal(a, b), label)
    elif isinstance(a, dict) and isinstance(b, dict):
        require(set(a) == set(b), label)
        for k in a:
            assert_same(a[k], b[k], label + '/' + str(k))
    elif isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        require(len(a) == len(b), label)
        for i, (x, y) in enumerate(zip(a, b)):
            assert_same(x, y, label + '/' + str(i))
    else:
        require(a == b, label)


def restore_full_state(model, opt, scheduler, sampler, scaler, payload, device, *, allow_cpu_fixture=False) -> None:
    """No optimizer/scheduler/RNG reset; assert exact restored state before training."""
    require((device.type == 'cuda' and torch.cuda.device_count() == 1) or
            (allow_cpu_fixture and device.type == 'cpu'), 'RESTORE_REQUIRES_SINGLE_CUDA_GPU')
    model.load_state_dict(payload['model'], strict=True)
    opt.load_state_dict(payload['optimizer'])
    scheduler.load_state_dict(payload['scheduler'])
    sampler.set_state(payload['sampler_state'].cpu())
    torch.set_rng_state(payload['torch_cpu_rng'].cpu())
    if device.type == 'cuda':
        torch.cuda.set_rng_state_all([x.cpu() for x in payload['torch_cuda_rng']])
    random.setstate(payload['python_rng'])
    state = payload['numpy_rng']
    np.random.set_state((state[0], np.asarray(state[1], dtype=np.uint32),
                         state[2], state[3], state[4]))
    require(scaler is not None, 'FP16_SCALER_REQUIRED')
    scaler.load_state_dict(payload['grad_scaler_state'])
    assert_same(model.state_dict(), payload['model'], 'MODEL_RESTORE_DRIFT')
    assert_same(opt.state_dict(), payload['optimizer'], 'OPTIMIZER_RESTORE_DRIFT')
    assert_same(scheduler.state_dict(), payload['scheduler'], 'SCHEDULER_RESTORE_DRIFT')
    assert_same(sampler.get_state(), payload['sampler_state'], 'SAMPLER_RESTORE_DRIFT')
    assert_same(torch.get_rng_state(), payload['torch_cpu_rng'], 'TORCH_CPU_RNG_DRIFT')
    if device.type == 'cuda':
        assert_same(torch.cuda.get_rng_state_all(), payload['torch_cuda_rng'], 'TORCH_CUDA_RNG_DRIFT')
    assert_same(random.getstate(), payload['python_rng'], 'PYTHON_RNG_DRIFT')
    assert_same(np.random.get_state()[1], np.asarray(state[1], dtype=np.uint32),
                'NUMPY_RNG_DRIFT')
    assert_same(scaler.state_dict(), payload['grad_scaler_state'], 'SCALER_RESTORE_DRIFT')
    assert_adamw_at_step(opt.state_dict(), payload['step'])
    assert_schedule_at_step(scheduler.state_dict(), opt.state_dict(), payload['step'])


def authorized_lock(path: Path | None, sha: str | None, code: Path, parent_sha: str) -> dict:
    require(path is not None and sha is not None, 'NEW_SCIENCE_LOCK_NOT_ISSUED')
    require(len(sha) == 64 and sha_file(path) == sha, 'NEW_SCIENCE_LOCK_SHA_MISMATCH')
    lock = json_read(path)
    expected = {'authorization': 'OWNER_APPROVED_ONESHOT_EXPLORATORY',
                'run_id': RUN_ID, 'parent_checkpoint_sha256': parent_sha,
                'source_sha256': sha_file(code), 'original_science_lock_sha256': OLD_LOCK_SHA,
                'train_val_pack_sha256': PACK_SHA, 'start_step': START, 'end_step': END,
                'targets_per_step': TARGETS, 'precision': 'fp16', 'microbatch_windows': 8,
                'optimizer': 'RESTORE_ORIGINAL_ADAMW', 'lr_after_1024': 3e-5,
                'test_access': False, 'q1q2_v3': False,
                'free_colab_only': True}
    require(all(lock.get(k) == v for k, v in expected.items()),
            'NEW_SCIENCE_LOCK_FIELDS_MISMATCH')
    return lock


def import_frozen(trainer_path: Path, capacity_path: Path, eval_path: Path):
    """Import exact source modules by pinned Git blobs; old trainer.main() never called."""
    for key, path in (('trainer', trainer_path), ('capacity', capacity_path),
                      ('evaluator', eval_path)):
        require(git_blob(path) == PINNED_GIT_BLOBS[key], 'FROZEN_MODULE_BLOB_CHANGED:' + key)
    sys.path.insert(0, str(Path(capacity_path).parent))
    try:
        spec = importlib.util.spec_from_file_location('ttm_original_t4_a2_source', trainer_path)
        require(spec is not None and spec.loader is not None, 'FROZEN_IMPORT_FAILED')
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        try:
            spec.loader.exec_module(mod)
        except BaseException:
            sys.modules.pop(spec.name, None)
            raise
        require(mod.CHECKPOINT_STEPS == (256,512,768,1024) and
                mod.TOKENS_PER_STEP == TARGETS, 'FROZEN_TRAINER_CONTRACT_CHANGED')
        return mod
    finally:
        sys.path.pop(0)


def paired_val_decision(base_sums, final_sums, counts) -> dict:
    a, b, c = map(lambda x: np.asarray(x, dtype=np.float64),
                  (base_sums, final_sums, counts))
    require(a.shape == b.shape == c.shape == (256,) and np.all(c > 0) and
            np.all(np.isfinite(a)) and np.all(np.isfinite(b)), 'PAIRED_VAL_INPUT_INVALID')
    require(int(c.sum()) == 61122, 'VAL_TARGET_COUNT_CHANGED')
    delta = float((a.sum()-b.sum())/c.sum())
    rng = np.random.default_rng(20261109)
    sampled = []
    for _ in range(1000):
        ix = rng.integers(0, len(c), size=len(c))
        sampled.append(float((a[ix].sum()-b[ix].sum())/c[ix].sum()))
    lo, hi = map(float, np.quantile(sampled, [0.025, 0.975]))
    return {'schema':'ttm.t4.original1280.paired_val.v1',
            'baseline_step': START, 'endpoint_step':END,
            'baseline_nll':float(a.sum()/c.sum()),
            'endpoint_nll':float(b.sum()/c.sum()),
            'delta_nll':delta,'ci95':[lo,hi],
            'bootstrap_rounds':1000,'bootstrap_seed':20261109,
            'verdict':'TRAINING_HELPFUL_SIGNAL' if delta>0 and lo>0 else 'TRAINING_NOT_CLEARED',
            'scope':'EXPLORATORY_VALIDATION_ONLY_NO_TEST_NO_QUALITY_CLAIM'}


def run(args):
    code = Path(__file__)
    paths = {'p02':Path(args.p02), 'trainer':Path(args.trainer),
             'capacity':Path(args.capacity), 'evaluator':Path(args.evaluator)}
    checked_paths(paths)
    require(sha_file(args.pack_manifest) == MANIFEST_SHA, 'DATA_MANIFEST_SHA_MISMATCH')
    manifest = json_read(args.pack_manifest)
    require(manifest.get('npz_sha256') == PACK_SHA and manifest.get('contains_test') is False,
            'TRAIN_VAL_MANIFEST_MISMATCH')
    ready, logs, parent = checked_parent(Path(args.parent_dir))
    require(parent is not None, 'PARENT_NOT_LOADED')
    if args.mode == 'inspect':
        print('TTM_T4_ORIGINAL_PARENT=PASS_SHA_READY_STATE_CPU')
        print('TTM_T4_ORIGINAL_TRAINING=NOT_EXECUTED')
        return 0
    authorized_lock(Path(args.lock) if args.lock else None, args.lock_sha, code, PARENT_SHA)
    require(torch.cuda.is_available() and torch.cuda.device_count() == 1 and
            'T4' in torch.cuda.get_device_name(0), 'SINGLE_FREE_T4_GPU_REQUIRED')
    require(str(torch.__version__) == '2.14.1+cu130' and str(torch.version.cuda) == '13.0',
            'CUDA_PYTORCH_ENVIRONMENT_CHANGED')
    frozen = import_frozen(paths['trainer'], paths['capacity'], paths['evaluator'])
    require(sha_file(args.pack) == PACK_SHA, 'TRAIN_VAL_NPZ_SHA_MISMATCH')
    data, m = frozen.load_private_pack(args.pack, args.pack_manifest)
    require(m['npz_sha256'] == PACK_SHA, 'DATA_PACK_INVALID')
    device = torch.device('cuda')
    model, opt, scheduler, sampler, scaler = frozen.model_context(
        frozen.p02_module(str(paths['p02'])), device, 'fp16')
    output = Path(args.output)
    require(not output.is_symlink() and not output.parent.is_symlink(),
            'OUTPUT_SYMLINK_FORBIDDEN')
    if args.resume_ready:
        require(output.is_dir(), 'RESUME_RUN_ROOT_MISSING')
        claim = json_read(output/'CLAIM.json')
        require(claim.get('new_lock_sha256') == args.lock_sha and
                claim.get('run_id') == RUN_ID and claim.get('parent_sha256') == PARENT_SHA and
                claim.get('source_sha256') == sha_file(code), 'RESUME_CLAIM_MISMATCH')
        folder = Path(args.resume_ready)
        require(folder == output/'checkpoints'/f'step_{MID:04d}', 'RESUME_READY_PATH_NOT_ALLOWED')
        require((folder/'READY.json').is_file(), 'RESUME_NO_READY')
        successor_ready = json_read(folder/'READY.json')
        require(successor_ready.get('schema') == 'ttm.t4.ready.last.v1' and
                successor_ready.get('step') == MID and
                successor_ready.get('science_lock_sha256') == args.lock_sha and
                successor_ready.get('train_pack_sha256') == PACK_SHA, 'RESUME_READY_INVALID')
        successor_cp = folder/'checkpoint.pt'
        require(successor_cp.is_file() and not successor_cp.is_symlink() and
                sha_file(successor_cp) == successor_ready.get('sha256') and
                successor_cp.stat().st_size == successor_ready.get('bytes'),
                'RESUME_CHECKPOINT_SHA_INVALID')
        require(sha_file(folder/'progress.json') == successor_ready.get('progress_sha256'),
                'RESUME_PROGRESS_SHA_INVALID')
        successor_payload = torch.load(successor_cp,map_location='cpu',weights_only=True)
        require(successor_payload.get('step') == MID and
                successor_payload.get('successor_run_id') == RUN_ID and
                successor_payload.get('parent_checkpoint_sha256') == PARENT_SHA,
                'RESUME_SUCCESSOR_PAYLOAD_MISMATCH')
        assert_adamw_at_step(successor_payload['optimizer'], MID)
        assert_schedule_at_step(successor_payload['scheduler'],
                                successor_payload['optimizer'], MID)
        start, _ = frozen.checkpoint_load(folder, model, opt, scheduler, sampler, scaler,
                                          device, args.lock_sha, PACK_SHA)
        require(start == MID, 'RESUME_ONLY_1152_ALLOWED')
        previous = json_read(folder/'progress.json')
        logs = previous['records']
        require(len(logs) == MID and all(e['step'] == i+1 for i,e in enumerate(logs)),
                'RESUME_PROGRESS_DRIFT')
        baseline_file=output/'BASELINE_PRIVATE.json'
        require(sha_file(baseline_file)==claim.get('baseline_sha256'),
                'RESUME_BASELINE_SHA_MISMATCH')
        base = json_read(baseline_file)
        base_sums = np.asarray(base['model_story_loss_sums'], dtype=np.float64)
        counts = np.asarray(base['val_story_target_counts'], dtype=np.int64)
    else:
        require(not output.exists(), 'NEW_RUN_ID_ALREADY_EXISTS_NO_RERUN')
        restore_full_state(model, opt, scheduler, sampler, scaler, parent, device)
        # Preclaim baseline is read-only and never reads TEST. This does not update weights.
        base_sums = frozen.model_story_scores(model, data, device)
        counts = np.bincount(data['val_story_index'],
                             weights=data['val_count'], minlength=256).astype(np.int64)
        require(len(base_sums)==256 and int(counts.sum())==61122,
                'BASELINE_VAL_SCOPE_CHANGED')
        require(abs(float(base_sums.sum()/counts.sum())-3.522338851682218)<1e-4,
                'BASELINE_PARENT_VAL_NLL_DRIFT')
        output.mkdir(parents=True, exist_ok=False)
        json_new(output/'BASELINE_PRIVATE.json', {
            'schema':'ttm.t4.original1280.baseline.private.v1',
            'model_story_loss_sums':base_sums.tolist(),
            'val_story_target_counts':counts.tolist(),
            'source_checkpoint_sha256':PARENT_SHA})
        json_new(output/'CLAIM.json', {'schema':'ttm.t4.original1280.claim.v1',
                  'run_id':RUN_ID,'parent_sha256':PARENT_SHA,
                  'new_lock_sha256':args.lock_sha,'source_sha256':sha_file(code),
                  'baseline_sha256':sha_file(output/'BASELINE_PRIVATE.json'),
                  'step_start':START,'step_end':END,'test_used':False})
        start = START
    for step in range(start+1, END+1):
        loss, windows = frozen.train_one_step(model,opt,scheduler,sampler,scaler,
                                              data,device,'fp16',8)
        logs.append({'step':step,'train_loss':loss,'windows_drawn':windows,
                     'exact_scored_targets':TARGETS})
        if step in (MID,END):
            assert_adamw_at_step(opt.state_dict(),step)
            assert_schedule_at_step(scheduler.state_dict(),opt.state_dict(),step)
            observed = frozen.model_story_scores(model,data,device)
            logs[-1]['val_model_nll'] = float(observed.sum()/counts.sum())
            payload = frozen.checkpoint_payload(model,opt,scheduler,sampler,scaler,step,
                                                args.lock_sha,PACK_SHA,0.0,device)
            payload['successor_run_id'] = RUN_ID
            payload['parent_checkpoint_sha256'] = PARENT_SHA
            frozen.checkpoint_write(output,step,payload,logs,output/'scratch')
            print(f'TTM_T4_ORIGINAL_READY_STEP={step}',flush=True)
    result = paired_val_decision(base_sums,observed,counts)
    result.update({'run_id':RUN_ID,'status':'COMPLETED_REQUIRES_INDEPENDENT_ADJUDICATION',
                   'source_sha256':sha_file(code),'new_lock_sha256':args.lock_sha,
                   'parent_checkpoint_sha256':PARENT_SHA,'test_used':False,
                   'new_steps':END-START,'added_target_exposures':(END-START)*TARGETS})
    json_new(output/'RESULT_UNADJUDICATED.json',result)
    print('TTM_T4_ORIGINAL_1280=COMPLETED_UNADJUDICATED',flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode',choices=('inspect','execute'),default='inspect')
    for name in ('parent-dir','pack','pack-manifest','p02','trainer','capacity','evaluator','output'):
        ap.add_argument('--'+name,required=True)
    ap.add_argument('--lock')
    ap.add_argument('--lock-sha')
    ap.add_argument('--resume-ready')
    args=ap.parse_args()
    return run(args)


if __name__ == '__main__':
    sys.exit(main())
