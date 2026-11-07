"""Independent synthetic microbatch overfit verification, no corpus/TEST/IO."""
import json
import math
import torch
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src.p02.transformer_core import GPT, P02Config
from src.p03.train_loop import TrainConfig, scheduled_lr, train_fixed_batch


def main():
    torch.set_num_threads(2)
    torch.manual_seed(20261107)
    model = GPT(P02Config())
    x = torch.tensor([[10, 256, 2047, 12, 512, 1],
                      [10, 256, 2047, 12, 512, 1]], dtype=torch.long)
    y = torch.tensor([[256, 2047, 12, 512, 1, 13],
                      [256, 2047, 12, 512, 1, 13]], dtype=torch.long)
    before = model.tok.weight.detach().clone()
    cfg = TrainConfig(steps=90)
    metrics = train_fixed_batch(model, x, y, cfg)
    checks = {
        'microbatch_loss_under_005': metrics['final_loss'] < 0.05,
        'initial_to_final_ratio_under_01': metrics['final_loss'] < metrics['initial_loss']*0.1,
        'parameters_updated': bool(torch.count_nonzero(before != model.tok.weight).item()),
        'all_parameters_finite': all(bool(torch.isfinite(p).all().item()) for p in model.parameters()),
        'schedule_positive_and_bounded': all(0 < scheduled_lr(s,cfg) <= cfg.peak_lr + 1e-12 for s in range(cfg.steps)),
        'no_checkpoint_saved': metrics['checkpoint'] == 'NOT_SAVED_P04_NOT_OPENED',
        'high_token_id_in_training': 2047 in x,
    }
    ok=all(checks.values())
    print(json.dumps({'schema':'ttm.p03.independent.synthetic_overfit.v1',
        'status':'PASS' if ok else 'FAIL','torch':torch.__version__,
        'checks':checks, 'initial_loss':metrics['initial_loss'],
        'final_loss':metrics['final_loss'],
        'no_corpus_read':True,'P04':'NOT_EXECUTED'},sort_keys=True))
    return 0 if ok else 1

if __name__=='__main__':
    raise SystemExit(main())
