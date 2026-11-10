#!/usr/bin/env python3
"""TTM-Small4M 2x2 *SYNTHETIC-ONLY* sampler / loss feasibility checks.

This is not a trainer: no optimizer, checkpoint, private TRAIN/VAL pack or generation.
All windows are invented deterministically. The 128x4096 budget is metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, replace
from pathlib import Path

import torch
from torch.nn import functional as F

VOCAB = 2048
CONTEXT = 256
BUDGET = 4096
STEPS = 128
MICROBATCH = 8
SYNTHETIC_SEED = 20261110


class ContractError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


@dataclass(frozen=True)
class Window:
    window_id: str
    story_id: int
    offset: int
    split: str
    count: int
    x: tuple[int, ...]
    y: tuple[int, ...]


@dataclass(frozen=True)
class Draw:
    window_index: int
    scored: int


def make_window(story_id: int, offset: int, count: int, split: str = 'TRAIN') -> Window:
    require(0 < count <= CONTEXT, 'INVALID_SYNTHETIC_COUNT')
    x = [((story_id * 73 + offset * 7 + k * 11) % (VOCAB - 300)) + 300 for k in range(count)]
    x += [0] * (CONTEXT - count)
    y = x[1:count] + [256] + [-100] * (CONTEXT - count)
    return Window(f'S{story_id:03d}-O{offset:03d}', story_id, offset, split,
                  count, tuple(x), tuple(y))


def synthetic_windows() -> list[Window]:
    """40 invented stories: first windows include several lengths and 256.

    Later windows deliberately lack first-story context; selection may change
    source-story frequency, while count and forward tensor shape remain fixed.
    """
    lens = (64, 91, 128, 176, 221, 256, 187, 256, 33, 245)
    out = [make_window(i, 0, lens[i % len(lens)]) for i in range(40)]
    out += [make_window(i, 256, (i * 19) % 235 + 18) for i in range(24)]
    return out


def validate_windows(windows: list[Window]) -> None:
    require(len(windows) >= 2, 'NOT_ENOUGH_WINDOWS')
    ids = set()
    for w in windows:
        require(w.split == 'TRAIN', 'NON_TRAIN_WINDOW_FORBIDDEN')
        require(isinstance(w.story_id, int) and w.story_id >= 0,
                'INVALID_STORY_INDEX')
        require(isinstance(w.offset, int) and w.offset >= 0 and w.offset % CONTEXT == 0,
                'INVALID_WINDOW_OFFSET')
        require(isinstance(w.window_id, str) and bool(w.window_id) and w.window_id not in ids,
                'DUPLICATE_OR_INVALID_WINDOW_ID')
        ids.add(w.window_id)
        require(isinstance(w.count, int) and 1 <= w.count <= CONTEXT,
                'INVALID_WINDOW_COUNT')
        require(len(w.x) == CONTEXT and len(w.y) == CONTEXT, 'INVALID_CONTEXT_SHAPE')
        require(all(isinstance(t, int) and 0 <= t < VOCAB for t in w.x),
                'INPUT_TOKEN_OUT_OF_VOCAB')
        require(all(isinstance(t, int) and 0 <= t < VOCAB for t in w.y[:w.count]),
                'LABEL_OUT_OF_VOCAB')
        require(all(t == -100 for t in w.y[w.count:]), 'INVALID_PADDING_MASK')
        require(all(w.y[i] == w.x[i + 1] for i in range(w.count - 1)),
                'NEXT_TOKEN_LABEL_SHIFT_INVALID')
        require(all(t == 0 for t in w.x[w.count:]), 'INPUT_PAD_LAYOUT_INVALID')
    # Each story has exactly one first window in the synthetic fixture.
    first_ids = [w.story_id for w in windows if w.offset == 0]
    require(len(first_ids) == len(set(first_ids)), 'MULTIPLE_FIRST_WINDOWS_PER_STORY')
    require(len(first_ids) > 0, 'NO_FIRST_STORY_WINDOWS')


def baseline_step(windows: list[Window], sampler: torch.Generator) -> tuple[Draw, ...]:
    total = 0
    result = []
    while total < BUDGET:
        ix = int(torch.randint(len(windows), (1,), generator=sampler).item())
        n = min(windows[ix].count, BUDGET - total)
        require(n > 0, 'EMPTY_BASELINE_DRAW')
        result.append(Draw(ix, n))
        total += n
    require(total == BUDGET, 'BASELINE_BUDGET_NOT_MET')
    return tuple(result)


def first_story_replace(windows: list[Window], baseline: tuple[Draw, ...],
                        *, step: int, seed: int = SYNTHETIC_SEED) -> tuple[Draw, ...]:
    require(isinstance(step, int) and step >= 1025, 'INVALID_STEP_INDEX')
    # Validated TRAIN-only source; fail closed if a late field was corrupted.
    validate_windows(windows)
    out = []
    for draw_idx, d in enumerate(baseline):
        require(0 <= d.window_index < len(windows), 'BASELINE_WINDOW_INDEX_INVALID')
        require(1 <= d.scored <= windows[d.window_index].count,
                'BASELINE_DRAW_COUNT_INVALID')
        matches = [i for i, w in enumerate(windows)
                   if w.offset == 0 and w.split == 'TRAIN' and w.count >= d.scored]
        require(bool(matches), 'NO_COUNT_MATCHED_FIRST_STORY_WINDOW')
        # Deterministic, per (step,draw,candidate) without dependence on global RNG.
        def key(i: int) -> bytes:
            s = f'{seed}|{step}|{draw_idx}|{windows[i].window_id}'.encode('ascii')
            return hashlib.sha256(s).digest()
        ix = min(matches, key=key)
        out.append(Draw(ix, d.scored))
    require(len(out) == len(baseline) and
            tuple(d.scored for d in out) == tuple(d.scored for d in baseline),
            'REPLACEMENT_NOT_COUNT_MATCHED')
    return tuple(out)


def validate_draw_plan(windows: list[Window], plan: tuple[Draw, ...],
                       *, first_only: bool = False) -> None:
    validate_windows(windows)
    require(bool(plan), 'EMPTY_DRAW_PLAN')
    total = 0
    for d in plan:
        require(isinstance(d, Draw) and isinstance(d.window_index, int)
                and isinstance(d.scored, int), 'INVALID_DRAW_TYPE')
        require(0 <= d.window_index < len(windows), 'WINDOW_INDEX_OUTSIDE_PACK')
        w = windows[d.window_index]
        require(1 <= d.scored <= w.count, 'DRAW_EXCEEDS_VALID_LABELS')
        require(not first_only or w.offset == 0, 'NOT_FIRST_STORY_WINDOW')
        total += d.scored
    require(total == BUDGET, 'WRONG_PER_STEP_VALID_TARGET_BUDGET')


def arm_layout(windows: list[Window], baseline: tuple[Draw, ...],
               first: tuple[Draw, ...]) -> dict[str, tuple[Draw, ...]]:
    validate_draw_plan(windows, baseline, first_only=False)
    validate_draw_plan(windows, first, first_only=True)
    require(len(baseline) == len(first) and
            tuple(x.scored for x in baseline) == tuple(x.scored for x in first),
            'UNFAIR_FORWARD_SCHEDULE')
    return {'A': baseline, 'B': first, 'C': baseline, 'D': first}


def hash_plan(plan: tuple[Draw, ...]) -> str:
    body = ','.join(f'{d.window_index}:{d.scored}' for d in plan).encode('ascii')
    return hashlib.sha256(body).hexdigest()


def masked_targets(windows: list[Window], plan: tuple[Draw, ...]) -> torch.Tensor:
    validate_draw_plan(windows, plan)
    rows=[]
    for d in plan:
        w=windows[d.window_index]
        rows.append(list(w.y[:d.scored]) + [-100] * (CONTEXT - d.scored))
    return torch.tensor(rows, dtype=torch.long)


def weighted_step_loss(logits: torch.Tensor, labels: torch.Tensor,
                       *, suffix_weighted: bool) -> torch.Tensor:
    """One scalar loss normalized over ALL valid tokens in the optimizer step.

    No optimizer, backward or checkpoint writing is performed by this function.
    """
    require(logits.ndim == 3 and labels.ndim == 2 and
            tuple(logits.shape[:2]) == tuple(labels.shape) and
            labels.shape[1] == CONTEXT and logits.shape[2] >= 2,
            'LOSS_LOGIT_LABEL_SHAPE_INVALID')
    require(logits.is_floating_point() and torch.isfinite(logits).all().item(),
            'LOSS_NONFINITE_LOGITS')
    require(torch.all((labels == -100) | ((labels >= 0) & (labels < logits.shape[2]))).item(),
            'LOSS_BAD_LABEL_ID')
    valid=labels.ne(-100)
    require(valid.any().item(), 'LOSS_NO_VALID_LABELS')
    loss=F.cross_entropy(logits.float().reshape(-1, logits.shape[-1]),
                         labels.reshape(-1), reduction='none',ignore_index=-100)
    loss=loss.reshape(labels.shape)
    weights=torch.ones_like(loss)
    if suffix_weighted:
        positions=torch.arange(CONTEXT,device=labels.device).view(1,-1)
        weights=torch.where(positions>=32, 3.0,1.0).to(loss.dtype).expand_as(loss)
    weights=weights * valid.to(loss.dtype)
    # This normalization is intentionally DIFFERENT from weighted loss / 4096.
    return (weights*loss).sum()/weights.sum()


def synthetic_run() -> dict:
    windows=synthetic_windows()
    validate_windows(windows)
    sampler=torch.Generator(device='cpu').manual_seed(SYNTHETIC_SEED)
    total={a:0 for a in 'ABCD'}
    forwards={a:0 for a in 'ABCD'}
    slots={a:0 for a in 'ABCD'}
    by_step=[]
    changed=0
    total_first={a:0 for a in 'ABCD'}
    hashed={a:hashlib.sha256() for a in 'ABCD'}
    for step in range(1025,1153):
        base=baseline_step(windows,sampler)
        first=first_story_replace(windows,base,step=step)
        arms=arm_layout(windows,base,first)
        record={'step':step}
        for a,plan in arms.items():
            require(sum(d.scored for d in plan)==BUDGET, 'ARM_STEP_BUDGET_ERROR')
            targets=sum(d.scored for d in plan)
            forwards[a]+=len(plan)
            slots[a]+=len(plan)*CONTEXT
            total[a]+=targets
            total_first[a]+=sum(windows[d.window_index].offset==0 for d in plan)
            hashed[a].update(bytes.fromhex(hash_plan(plan)))
            record[a]={'draws':len(plan),'targets':targets,'slots':len(plan)*CONTEXT,
                       'microbatches':(len(plan)+MICROBATCH-1)//MICROBATCH,
                       'plan_sha256':hash_plan(plan)}
        require(record['A']['plan_sha256']==record['C']['plan_sha256'],
                'CONTROL_OBJECTIVE_PLANS_DIFFER')
        require(record['B']['plan_sha256']==record['D']['plan_sha256'],
                'DATA_OBJECTIVE_PLANS_DIFFER')
        require(all(record[a]['draws']==record['A']['draws'] and
                    record[a]['slots']==record['A']['slots'] and
                    record[a]['microbatches']==record['A']['microbatches']
                    for a in 'ABCD'), 'UNFAIR_SHAPE_OR_MICROBATCH')
        changed+=sum(u.window_index != v.window_index for u,v in zip(base,first))
        by_step.append(record)
    require(all(x==STEPS*BUDGET for x in total.values()),
            'TOTAL_TARGET_BUDGET_FAILURE')
    require(len(set(forwards.values()))==1 and len(set(slots.values()))==1,
            'FORWARD_SLOTS_NOT_MATCHED')
    require(hashed['A'].digest()==hashed['C'].digest() and
            hashed['B'].digest()==hashed['D'].digest(),
            'ARM_PAIR_SCHEDULE_DRIFT')
    return {
       'schema':'ttm.small4m.2x2.synthetic_preflight.result.v1',
       'status':'SYNTHETIC_SAMPLER_PASS_NOT_TRAINING',
       'synthetic_seed':SYNTHETIC_SEED,'synthetic_train_stories':40,
       'synthetic_total_windows':len(windows),
       'steps':STEPS,'targets_per_step':BUDGET,'microbatch_windows':MICROBATCH,
       'total_valid_label_exposures':total,
       'total_forward_windows':forwards,
       'total_forward_token_slots':slots,
       'first_story_window_draw_counts':total_first,
       'replacement_count_changed_window_id':changed,
       'plan_digest_by_arm':{a:hashed[a].hexdigest() for a in 'ABCD'},
       'per_step':by_step,
       'source_dataset':'SYNTHETIC_INVENTED_ONLY',
       'real_TRAIN_VAL_pack_read':False,'model_weights_loaded':False,
       'optimizer_updates':0,'GPU_training':False,'science_inference':False,
       'caveat':'Matching feasibility on real locked TRAIN pack NOT ESTABLISHED'
    }


def cli() -> None:
    p=argparse.ArgumentParser()
    p.add_argument('--mode',choices=('synthetic','none'),default='none')
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    require(args.mode=='synthetic','SYNTHETIC_MODE_EXPLICITLY_REQUIRED')
    r=synthetic_run()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x',encoding='utf8') as f:
            json.dump(r,f,sort_keys=True,indent=2)
            f.write('\n')
    print('TTM_2X2_SYNTHETIC_SAMPLER=PASS')
    print('VALID_EXPOSURES_PER_ARM='+str(r['total_valid_label_exposures']))
    print('TOTAL_FORWARD_WINDOWS='+str(r['total_forward_windows']))
    print('REAL_TRAINING=NOT_EXECUTED')


if __name__=='__main__':
    cli()
