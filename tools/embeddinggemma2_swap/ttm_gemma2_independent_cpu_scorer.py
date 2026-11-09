#!/usr/bin/env python3
"""Independent CPU next-token NLL scorer contract; only synthetic fixture is executable.

The production checkpoint-to-model adapter is NOT connected in this design-only phase.
No model weights, private story IDs or actual evaluation data are loaded here.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
import math
import torch
import torch.nn.functional as F

VOCAB = 2048
CONTEXT = 256
ALLOWED_SPLIT = 'NEW_HOLDOUT'


def insist(condition, message):
    if not condition:
        raise RuntimeError('STOP_EVAL_' + message)


def score_story_windows(model, rows, *, vocab=VOCAB):
    """Model-agnostic CPU scorer; rows=(story_id, split, input_ids, target_ids).

    Each input/target tensor is 1D with 256 slots. PAD labels are -100. A story
    may have multiple contiguous non-overlapping windows; source contract owns
    the window/order construction, and must audit it independently before scoring.
    """
    insist(all(p.device.type == 'cpu' for p in model.parameters()), 'MODEL_NOT_CPU')
    model.eval()
    sums = defaultdict(float)
    counts = defaultdict(int)
    with torch.inference_mode():
        for story_id, split, x, y in rows:
            insist(split == ALLOWED_SPLIT, 'OLD_SPLIT_OR_TEST_FORBIDDEN')
            insist(isinstance(story_id, str) and len(story_id) == 64 and all(c in '0123456789abcdef' for c in story_id), 'STORY_ID')
            insist(x.device.type == y.device.type == 'cpu', 'GPU_FORBIDDEN')
            insist(x.dtype == torch.long and y.dtype == torch.long, 'ID_DTYPE')
            insist(x.ndim == y.ndim == 1 and x.shape == y.shape == (CONTEXT,), 'WINDOW_SHAPE')
            mask = y != -100
            n = int(mask.sum().item())
            insist(n > 0 and torch.all((y[mask] >= 0) & (y[mask] < vocab)).item(), 'LABEL_RANGE_OR_EMPTY')
            insist(torch.all((x >= 0) & (x < vocab)).item(), 'INPUT_RANGE')
            z = model(x[None, :])
            if isinstance(z, dict):
                z = z['logits']
            insist(isinstance(z, torch.Tensor) and z.shape == (1, CONTEXT, vocab), 'LOGIT_SHAPE')
            insist(z.device.type == 'cpu' and torch.isfinite(z).all().item(), 'LOGIT_FINITE_CPU')
            loss = F.cross_entropy(z[0].to(torch.float64), y[None, :].reshape(-1), ignore_index=-100, reduction='sum')
            insist(torch.isfinite(loss).item(), 'LOSS_NONFINITE')
            sums[story_id] += float(loss.item())
            counts[story_id] += n
    insist(bool(sums) and sum(counts.values()) > 0, 'EMPTY_SCORING')
    return {'stories':len(sums),'target_count':sum(counts.values()),'loss_sums_by_story':dict(sums),'counts_by_story':dict(counts),
            'nll_per_target':sum(sums.values()) / sum(counts.values())}


def fixture_qa():
    checks = {}
    def ok(name, predicate):
        assert predicate, name
        checks[name] = 'PASS'
    def fails(f):
        try:
            f()
            return False
        except RuntimeError:
            return True
    class SyntheticLogits(torch.nn.Module):
        def forward(self, ids):
            b,t=ids.shape
            return torch.zeros((b,t,VOCAB),dtype=torch.float32)
    model = SyntheticLogits()
    key = '0' * 64
    x = torch.zeros(CONTEXT,dtype=torch.long)
    y = torch.full((CONTEXT,),-100,dtype=torch.long)
    y[:2] = torch.tensor([1,2])
    rows=[(key,ALLOWED_SPLIT,x,y)]
    good=score_story_windows(model,rows)
    ok('uniform_NLL_log_vocab',abs(good['nll_per_target']-math.log(VOCAB))<1e-11)
    ok('two_targets_not_padding',good['target_count']==2)
    ok('one_story',good['stories']==1)
    ok('TEST_rejected',fails(lambda:score_story_windows(model,[(key,'TEST',x,y)])))
    ok('VAL_rejected',fails(lambda:score_story_windows(model,[(key,'VAL',x,y)])))
    ok('short_id_rejected',fails(lambda:score_story_windows(model,[('x',ALLOWED_SPLIT,x,y)])))
    ok('empty_target_rejected',fails(lambda:score_story_windows(model,[(key,ALLOWED_SPLIT,x,torch.full_like(y,-100))])))
    bad_y=y.clone();bad_y[0]=VOCAB
    ok('out_of_vocab_rejected',fails(lambda:score_story_windows(model,[(key,ALLOWED_SPLIT,x,bad_y)])))
    ok('bad_shape_rejected',fails(lambda:score_story_windows(model,[(key,ALLOWED_SPLIT,x[:7],y[:7])])))
    ok('bad_dtype_rejected',fails(lambda:score_story_windows(model,[(key,ALLOWED_SPLIT,x.float(),y)])))
    ok('two_windows_accumulate_same_story',score_story_windows(model,rows+rows)['target_count']==4)
    class NanLogits(torch.nn.Module):
        def forward(self, ids):return torch.full((1,CONTEXT,VOCAB),float('nan'))
    ok('NaN_logits_rejected',fails(lambda:score_story_windows(NanLogits(),rows)))
    return {'schema':'ttm.gemma2.cpu_scorer.synthetic_qa.v1','status':'PASS','passed':len(checks),'total':len(checks),
            'checks':checks,'gpu_used':False,'real_checkpoint_loaded':False,'new_holdout_scored':False,
            'model_binding':'NOT_CONNECTED_DESIGN_ONLY'}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['fixture-qa'],required=True)
    args=ap.parse_args()
    print(json.dumps(fixture_qa(),sort_keys=True,ensure_ascii=False))

if __name__ == '__main__':
    main()
