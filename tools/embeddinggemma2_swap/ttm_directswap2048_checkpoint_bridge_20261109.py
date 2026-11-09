#!/usr/bin/env python3
"""Owner-amended TTM GPU2048: bridge exactly four frozen GPU1024 AdamW states.

The CPU preflight is read-only. GPU execution requires one NEW claim/RUN_ID;
only optimizer steps 1025..2048 are allowed. Parent artifacts are read-only.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch

import ttm_directswap2048_gpu_once as core

PARENT_RUN_ID = 'ttm_small4m_gemma2_directswap_1024x4096_t4_gpu_20261109_v1'
RUN_ID = 'ttm_small4m_gemma2_directswap_2048x4096_t4_gpu_20261109_v1'
AMENDMENT_COMMIT = '24d0b7b1d5eea590ba1cfa0d00f74ffcbdd6f72a'
PARENT_SOURCE_SHA = '00416c0ff5b2afdcca2780a20315dd2da0af93554cd2b32b6c94efb630dc5d3b'
PARENT_CLAIM_SHA = 'd7e99b831dcb69688e4a1483732f174125f8e1a10d5e73cea5c4ef9efcfb3011'
PARENT_RESULT_SHA = '46a93c888063c27711541c067d168ded31bbf22f6c46ba6efe45051cdc9c0bec'
PARENT_PREFIX_SHA = '19ddc05128c188b86bda2f02de6389946944fe287c26abbf7d24cc5f9681e8f2'
FULL_SCHEDULE_SHA = '81e4834f991607e8c3143bb67ed4a9ade93faa5f9526f630dc79e85bb0e51a52'
CORE_SOURCE_SHA = '0994f0cd91cb504f2db8478f55963813a85469807f2921e38c196248f323759e'
PARENT_STEP = 1024
NEW_MILESTONES = (1280, 1536, 1792, 2048)
PARENT_CHECKPOINTS = {
    'A': ('95bb69de752bf051958f0d8e19a388528d2cc102f02258c88d756526a9406aa2', 45100187),
    'B': ('8ecca1e181726965d4f6e76c8e725b612706d5242accd408a9386964939191d1', 51393267),
    'C': ('cb77a5c2e435dd8cf1f61259f560a22964bc8c8c06889b0494cb961ed76bc9ac', 52969605),
    'D': ('81003fa2fe194a7e22b30d1b3e330fc65ec0ae486a08511d17c367ec5c25f69f', 52969605),
}
assert RUN_ID == core.RUN_ID and core.STEPS == 2048
assert core.LABELS_PER_STEP == 4096 and core.MICROBATCH_WINDOWS == 8
core.CHECKPOINT_STEPS = NEW_MILESTONES


def insist(condition: bool, why: str) -> None:
    if not condition:
        raise RuntimeError('STOP_BRIDGE_' + why)


def exact_schedule(schedule, schedule_sha: str) -> None:
    insist(len(schedule) == 2048, 'TOTAL_SCHEDULE_LENGTH')
    insist(schedule_sha == FULL_SCHEDULE_SHA, 'FULL_SCHEDULE_SHA')
    insist(hashlib.sha256(core.canonical(schedule[:PARENT_STEP])).hexdigest() == PARENT_PREFIX_SHA,
           '1024_STEP_SCHEDULE_PREFIX_MISMATCH')
    insist(all(sum(lim) == 4096 and len(ids) == len(lim) for ids, lim in schedule),
           'EQUAL_TRAIN_TARGETS')


def exact_parent(parent: Path, schedule, current_env: dict) -> dict:
    """Read original files and return small pins; no writes anywhere."""
    insist(not parent.is_symlink() and parent.is_dir() and parent.name == PARENT_RUN_ID,
           'PARENT_ROOT')
    claim_path, result_path = parent / 'CLAIM.json', parent / 'RESULT.json'
    insist(claim_path.is_file() and core.sha_file(claim_path) == PARENT_CLAIM_SHA,
           'PARENT_CLAIM_SHA')
    insist(result_path.is_file() and core.sha_file(result_path) == PARENT_RESULT_SHA,
           'PARENT_RESULT_SHA')
    claim = json.loads(claim_path.read_text('utf-8'))
    result = json.loads(result_path.read_text('utf-8'))
    insist(claim.get('run_id') == PARENT_RUN_ID and result.get('run_id') == PARENT_RUN_ID,
           'PARENT_RUN_ID')
    insist(result.get('status') == 'COMPLETED_UNADJUDICATED', 'PARENT_COMPLETE')
    insist(claim.get('source_sha256') == PARENT_SOURCE_SHA and
           claim.get('train_schedule_sha256') == PARENT_PREFIX_SHA and
           result.get('train_schedule_sha256') == PARENT_PREFIX_SHA, 'PARENT_SOURCE_SCHEDULE')
    insist(claim.get('steps_per_arm') == 1024 and claim.get('labels_per_step') == 4096 and
           claim.get('target_exposures_per_arm') == 4194304, 'PARENT_EXPOSURES')
    insist(claim.get('pins') == core.PINS and result.get('source_inputs_sha256') == core.PINS,
           'PARENT_INPUT_PINS')
    insist(claim.get('environment') == current_env, 'PARENT_RUNTIME_MISMATCH')
    # Ground the old sampling schedule itself, not only its hash in CLAIM.
    old_schedule = parent / 'TRAIN_SCHEDULE_PRIVATE.json'
    insist(old_schedule.is_file() and not old_schedule.is_symlink(), 'PARENT_SCHEDULE_FILE_MISSING')
    prev = json.loads(old_schedule.read_text('utf-8'))
    insist(prev.get('run_id') == PARENT_RUN_ID and prev.get('sha256') == PARENT_PREFIX_SHA,
           'PARENT_SCHEDULE_META')
    insist(prev.get('schedule') == [list(pair) for pair in schedule[:PARENT_STEP]],
           'PARENT_SCHEDULE_BYTES_SEMANTIC_MISMATCH')
    paths = {}
    for arm, (digest, size) in PARENT_CHECKPOINTS.items():
        d = parent / 'checkpoints' / arm / 'step_1024_attempt_00'
        ready_path, cp = d / 'READY.json', d / 'checkpoint.pt'
        insist(not d.is_symlink() and not cp.is_symlink() and ready_path.is_file(),
               'PARENT_READY_MISSING_' + arm)
        insist(cp.is_file() and cp.stat().st_size == size and core.sha_file(cp) == digest,
               'PARENT_CKPT_SHA_' + arm)
        r = json.loads(ready_path.read_text('utf-8'))
        insist(r.get('schema') == 'ttm.gemma2.directswap1024.checkpoint.ready.last.v1' and
               r.get('arm') == arm and r.get('step') == PARENT_STEP and
               r.get('run_id') == PARENT_RUN_ID and r.get('source_sha256') == PARENT_SOURCE_SHA and
               r.get('schedule_sha256') == PARENT_PREFIX_SHA and
               r.get('checkpoint_sha256') == digest and r.get('checkpoint_bytes') == size,
               'PARENT_READY_META_' + arm)
        insist(result.get('final_checkpoint_sha256', {}).get(arm) == digest,
               'PARENT_FINAL_RESULT_SHA_' + arm)
        paths[arm] = cp
    insist(set(paths) == set(core.ARMS), 'MISSING_ARM')
    return {'parent_run_id': PARENT_RUN_ID, 'parent_claim_sha256': PARENT_CLAIM_SHA,
            'parent_result_sha256': PARENT_RESULT_SHA, 'parent_source_sha256': PARENT_SOURCE_SHA,
            'parent_schedule_sha256': PARENT_PREFIX_SHA,
            'parent_checkpoint_sha256': {k: v[0] for k, v in PARENT_CHECKPOINTS.items()},
            'parent_gpu_seconds': float(result['gpu_seconds_cumulative'])}


def validate_payload(arm: str, p: dict) -> None:
    insist(p.get('schema') == 'ttm.gemma2.directswap1024.gpu.resumable.checkpoint.v1',
           'PAYLOAD_SCHEMA_' + arm)
    insist(p.get('run_id') == PARENT_RUN_ID and p.get('arm') == arm and
           p.get('step') == PARENT_STEP, 'PAYLOAD_ID_STEP_' + arm)
    insist(p.get('source_sha256') == PARENT_SOURCE_SHA and
           p.get('schedule_sha256') == PARENT_PREFIX_SHA and
           p.get('input_sha256') == core.PINS, 'PAYLOAD_FINGERPRINT_' + arm)
    losses = p.get('train_losses')
    insist(isinstance(losses, list) and len(losses) == 1024 and
           all(isinstance(v, (int, float)) and math.isfinite(v) for v in losses),
           'PAYLOAD_LOSS_HISTORY_' + arm)
    insist(isinstance(p.get('model'), dict) and bool(p['model']), 'PAYLOAD_MODEL_' + arm)
    opt = p.get('optimizer', {})
    groups = opt.get('param_groups', [])
    insist(len(groups) == 1 and opt.get('state'), 'PAYLOAD_OPTIMIZER_' + arm)
    group = groups[0]
    insist(float(group['lr']) == 1e-4 and tuple(group['betas']) == (0.9, 0.95) and
           float(group['eps']) == 1e-8 and float(group['weight_decay']) == 0.1,
           'PAYLOAD_OPTIMIZER_CONFIG_' + arm)
    insist(len(group['params']) == len(opt['state']), 'PAYLOAD_OPTIMIZER_MISSING_STATE_' + arm)
    insist(all(float(s.get('step', -1)) == PARENT_STEP and
               'exp_avg' in s and 'exp_avg_sq' in s for s in opt['state'].values()),
           'PAYLOAD_OPTIMIZER_STEP_' + arm)
    insist(isinstance(p.get('torch_rng_cpu'), torch.Tensor) and
           p['torch_rng_cpu'].dtype == torch.uint8, 'PAYLOAD_CPU_RNG_' + arm)
    cuda_rng = p.get('torch_rng_cuda')
    insist(isinstance(cuda_rng, list) and len(cuda_rng) == 1 and
           isinstance(cuda_rng[0], torch.Tensor) and cuda_rng[0].dtype == torch.uint8,
           'PAYLOAD_CUDA_RNG_' + arm)
    insist(math.isfinite(float(p.get('gpu_seconds_cumulative', -1))) and
           float(p['gpu_seconds_cumulative']) > 0, 'PAYLOAD_GPU_SECONDS_' + arm)


def restore_original(arm: str, cp: Path, model, optimizer) -> tuple[list, dict]:
    p = torch.load(cp, map_location='cpu', weights_only=True)
    validate_payload(arm, p)
    model.load_state_dict(p['model'], strict=True)
    optimizer.load_state_dict(p['optimizer'])
    # Check mapping between optimizer state and the current model parameter list.
    trainable = [x for x in model.parameters() if x.requires_grad]
    insist(len(trainable) == len(optimizer.state), 'OPT_PARAMETER_COUNT_' + arm)
    insist(all(float(s.get('step', -1)) == 1024 for s in optimizer.state.values()),
           'RESTORED_OPTIMIZER_STEPS_' + arm)
    torch.set_rng_state(p['torch_rng_cpu'].cpu())
    torch.cuda.set_rng_state_all([x.cpu() for x in p['torch_rng_cuda']])
    return list(p['train_losses']), {
        'arm': arm, 'imported_step': 1024, 'checkpoint_sha256': PARENT_CHECKPOINTS[arm][0],
        'optimizer_steps_verified': 1024, 'rng_cpu_cuda_restored': True,
        'original_gpu_seconds': float(p['gpu_seconds_cumulative'])}


def build_claim(env, bridge_sha, core_sha, schedule_sha, bridge_receipt):
    return {
        'schema': 'ttm.gemma2.directswap2048.gpu.bridge.claim.v1',
        'run_id': RUN_ID, 'parent_run_id': PARENT_RUN_ID,
        'amendment_commit': AMENDMENT_COMMIT,
        'source_sha256': bridge_sha, 'core_runner_sha256': core_sha,
        'source_inputs_sha256': core.PINS,
        'parent': bridge_receipt,
        'train_schedule_sha256': schedule_sha, 'prefix_schedule_sha256': PARENT_PREFIX_SHA,
        'arms': list(core.ARMS), 'steps_per_arm_total': 2048,
        'already_consumed_steps_per_arm': 1024, 'new_steps_per_arm': 1024,
        'labels_per_step': 4096, 'new_targets_per_arm': 4194304,
        'optimizer': {'name': 'AdamW', 'lr': 0.0001, 'betas': [0.9, 0.95],
                      'eps': 1e-8, 'weight_decay': 0.1, 'grad_clip': 1.0},
        'bootstrap_seed': core.SEED, 'bootstrap_rounds': core.BOOT,
        'environment': env, 'gpu_seconds_cap_new': core.GPU_SECONDS_LIMIT,
        'no_test': True, 'validation_after_all_arms_only': True,
        'checkpoint_steps': list(NEW_MILESTONES),
    }


def execute(args):
    insist(args.parent != args.output and args.parent.name == PARENT_RUN_ID, 'PARENT_OUTPUT_OVERLAP')
    insist(not args.output.is_symlink() and not args.parent.is_symlink(), 'SYMLINK_ROOT')
    core.hash_and_require(Path(__file__), 'BRIDGE_SCRIPT', args.bridge_sha256)
    core.hash_and_require(Path(core.__file__), 'ORIGINAL_2048_CORE', CORE_SOURCE_SHA)
    torch.set_num_threads(2)
    torch.manual_seed(core.SEED)
    torch.cuda.manual_seed_all(core.SEED)
    data, ckpt, donor, sw, p02, schedule, schedule_sha = core.preclaim(args)
    exact_schedule(schedule, schedule_sha)
    env = {'torch': torch.__version__, 'cuda': torch.version.cuda,
           'gpu_name': torch.cuda.get_device_name(0),
           'precision': 'CUDA_FP32_NO_TF32', 'microbatch_windows': core.MICROBATCH_WINDOWS}
    bridge = exact_parent(args.parent, schedule, env)
    claim = build_claim(env, args.bridge_sha256, CORE_SOURCE_SHA, schedule_sha, bridge)
    if args.resume:
        stored = json.loads((args.output / 'CLAIM.json').read_text('utf-8'))
        insist(stored == claim, 'RESUME_CLAIM_CHANGED')
    else:
        args.output.mkdir(parents=True, exist_ok=False)
        core.write_json_new(args.output / 'CLAIM.json', claim)
        core.write_json_new(args.output / 'BRIDGE_RECEIPT.json', bridge)
        core.write_json_new(args.output / 'TRAIN_SCHEDULE_PRIVATE.json',
                            {'run_id': RUN_ID, 'sha256': schedule_sha, 'schedule': schedule})
        print('TTM_GPU2048_BRIDGE_CLAIM=CONSUMED', flush=True)
    args.scratch.mkdir(parents=True, exist_ok=True)
    elapsed_new = 0.0
    device = torch.device('cuda:0')
    for arm in core.ARMS:
        model = core.build_model(arm, p02, sw, ckpt, donor).to(device=device, dtype=torch.float32)
        opt = core.new_optimizer(model)
        prior = core.latest_ready(args, arm, schedule_sha, args.bridge_sha256)
        marker_path = args.output / 'ARM_STARTS' / (arm + '.json')
        expected_marker = {'run_id': RUN_ID, 'parent_run_id': PARENT_RUN_ID,
                           'arm': arm, 'imported_step': 1024,
                           'checkpoint_sha256': PARENT_CHECKPOINTS[arm][0],
                           'source_sha256': args.bridge_sha256}
        if prior:
            insist(marker_path.is_file() and
                   json.loads(marker_path.read_text('utf-8')) == expected_marker,
                   'RESUME_MARKER_MISSING_OR_CHANGED_' + arm)
            step0, losses, recorded = core.restore_checkpoint(
                prior[1], model, opt, arm, schedule_sha, args.bridge_sha256)
            insist(step0 in NEW_MILESTONES and len(losses) == step0 and step0 >= 1280,
                   'NEW_READY_STEP_INVALID_' + arm)
            elapsed_new = max(elapsed_new, recorded)
            print(f'TTM_GPU2048_BRIDGE_RESUME arm={arm} step={step0}', flush=True)
        else:
            insist(not marker_path.exists(), 'STARTED_ARM_WITHOUT_READY_NO_AUTO_REPLAY_' + arm)
            source_cp = args.parent / 'checkpoints' / arm / 'step_1024_attempt_00' / 'checkpoint.pt'
            losses, receipt = restore_original(arm, source_cp, model, opt)
            insist(len(losses) == 1024, 'IMPORTED_LOSS_PREFIX_' + arm)
            # A marker precedes the first NEW optimizer update. Never reuse parent RUN_ID.
            marker_path.parent.mkdir(parents=True, exist_ok=True)
            core.write_json_new(marker_path, expected_marker)
            core.write_json_new(args.output / ('IMPORT_' + arm + '.json'), receipt)
            step0 = 1024
            print(f'TTM_GPU2048_BRIDGE_IMPORTED arm={arm} step=1024', flush=True)
        insist(elapsed_new < core.GPU_SECONDS_LIMIT, 'BUDGET_CAP_EXCEEDED')
        for step in range(step0 + 1, core.STEPS + 1):
            torch.cuda.synchronize()
            started = time.perf_counter()
            loss = core.train_one_step(model, opt, schedule[step-1], data, device)
            torch.cuda.synchronize()
            elapsed_new += time.perf_counter() - started
            losses.append(loss)
            if step in (1025, 1152, 1280, 1536, 1792, 2048):
                print(f'TTM_GPU2048_ARM={arm} STEP={step} TRAIN_LOSS={loss:.6f}',flush=True)
            if step in NEW_MILESTONES:
                core.save_checkpoint(args, arm, step, model, opt, losses,
                                     schedule_sha, elapsed_new, args.bridge_sha256)
            if elapsed_new >= core.GPU_SECONDS_LIMIT:
                print(f'TTM_GPU2048_STATUS=INCOMPLETE_BUDGET arm={arm} step={step}', flush=True)
                raise SystemExit(3)
        del model, opt
        torch.cuda.empty_cache()
    counts = np.bincount(data['val_story_index'], weights=data['val_count'],
                         minlength=256).astype(np.int64)
    insist(np.all(counts > 0) and counts.sum() == 61122, 'VAL_TARGETS_STORIES')
    loss_sums, hashes = {}, {}
    for arm in core.ARMS:
        model = core.build_model(arm, p02, sw, ckpt, donor).to(device=device, dtype=torch.float32)
        done = core.latest_ready(args, arm, schedule_sha, args.bridge_sha256)
        insist(done is not None and done[0] == 2048, 'INCOMPLETE_ARM_NO_VAL_' + arm)
        state = torch.load(done[1]/'checkpoint.pt', map_location='cpu', weights_only=True)
        model.load_state_dict(state['model'], strict=True)
        loss_sums[arm] = core.val_story_sums(model, data, device)
        hashes[arm] = core.sha_file(done[1]/'checkpoint.pt')
        print(f'TTM_GPU2048_FINAL_NLL arm={arm} nll={loss_sums[arm].sum()/61122:.9f}',flush=True)
        del model
        torch.cuda.empty_cache()
    cis = {name: core.paired_ci(loss_sums[a],loss_sums['C'],counts)
           for name,a in (('A_minus_C','A'),('B_minus_C','B'),('D_minus_C','D'))}
    nll = {a: float(x.sum()/61122) for a,x in loss_sums.items()}
    gains = {name:nll[a]-nll['C'] for name,a in
             (('A_minus_C','A'),('B_minus_C','B'),('D_minus_C','D'))}
    positive = all(v[0] > 0 for v in cis.values())
    per_story = {'schema':'ttm.gemma2.directswap2048.bridge.private.perstory.v1',
                 'run_id':RUN_ID,'n_targets_by_story':counts.tolist(),
                 'loss_sums_by_arm':{a:x.tolist() for a,x in loss_sums.items()}}
    core.write_json_new(args.output/'PER_STORY_PRIVATE.json', per_story)
    result = {
        'schema':'ttm.gemma2.directswap2048.bridge.result.v1',
        'run_id':RUN_ID,'parent_run_id':PARENT_RUN_ID,
        'status':'COMPLETED_UNADJUDICATED',
        'exploratory_label':('DIRECT_SWAP_2048_POSITIVE_EXPLORATORY' if positive
                           else 'DIRECT_SWAP_2048_BENEFIT_NOT_ESTABLISHED'),
        'amendment_commit': AMENDMENT_COMMIT,
        'bridge_sha256':args.bridge_sha256,'core_sha256':CORE_SOURCE_SHA,
        'parent_checkpoint_sha256':{a:t[0] for a,t in PARENT_CHECKPOINTS.items()},
        'final_checkpoint_sha256':hashes,
        'train_schedule_sha256':schedule_sha,'imported_steps_per_arm':1024,
        'new_steps_per_arm':1024,'final_steps_per_arm':2048,
        'total_train_targets_per_arm':2048*4096,'added_train_targets_per_arm':1024*4096,
        'val_targets':61122,'val_stories':256,'val_windows':328,
        'nll_val':nll,'confidence_interval_95pct':cis,'nll_differences':gains,
        'per_story_sha256':core.sha_file(args.output/'PER_STORY_PRIVATE.json'),
        'gpu_seconds_added':elapsed_new,'gpu_seconds_parent':bridge['parent_gpu_seconds'],
        'test_read':False,'validation_scored_once_after_all_arms':True,
        'limitations':['Outcome-driven extension; repeated VALIDATION, one seed',
                       'Checkpoint continuation, not independent training',
                       'Equal steps/labels, not equal FLOPs']}
    core.write_json_new(args.output/'RESULT.json',result)
    print('TTM_GPU2048_STATUS=COMPLETED_UNADJUDICATED',flush=True)
    print('TTM_GPU2048_DRIVE_RESULT='+str(args.output/'RESULT.json'),flush=True)


def cli():
    p = argparse.ArgumentParser()
    for key in ('base','candidate','pack','manifest','source_dir','output','scratch','parent'):
        p.add_argument('--'+key.replace('_','-'),type=Path,required=True)
    p.add_argument('--runner-sha256',required=True)
    p.add_argument('--bridge-sha256',required=True)
    p.add_argument('--resume',action='store_true')
    args = p.parse_args()
    insist(args.runner_sha256 == CORE_SOURCE_SHA, 'CORE_CLI_SHA_PIN')
    return args

if __name__ == '__main__':
    execute(cli())
