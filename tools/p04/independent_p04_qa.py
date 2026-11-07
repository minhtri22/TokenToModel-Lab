"""Independent P04 synthetic QA; no dataset readers, optimizer, or P01 TEST."""
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import torch
from torch.nn import functional as F

from src.p02.transformer_core import GPT, P02Config
from src.p04.eval_checkpoints import (save_checkpoint_new, load_checkpoint_verified,
                                      generate_tokens, evaluate_synthetic_heldout)

BPE_SHA = "53aabcb8ac3a3c16c7cbd915b76eb82653a334c98381fad95a05eba0a9353f60"


def main() -> int:
    torch.set_num_threads(2)
    torch.manual_seed(404)
    model = GPT(P02Config()).eval()
    checks = {}
    with TemporaryDirectory(dir=ROOT) as d:
        p = Path(d) / "synthetic_weights.pt"
        sha = save_checkpoint_new(p, model, BPE_SHA)
        restored = load_checkpoint_verified(p, sha, BPE_SHA)
        checks["checkpoint_restores_exact_parameters"] = all(
            torch.equal(a, b) for a,b in zip(model.parameters(), restored.parameters()))
        try:
            load_checkpoint_verified(p, sha, "0"*64)
            checks["checkpoint_wrong_tokenizer_rejected"] = False
        except ValueError:
            checks["checkpoint_wrong_tokenizer_rejected"] = True
    prefix = [0, 256, 2047, 1034]
    generated = generate_tokens(model, prefix, 4, top_k=1, seed=404)
    ctx = prefix[:]
    oracle = prefix[:]
    with torch.inference_mode():
        for _ in range(4):
            logits, _ = model(torch.tensor([ctx], dtype=torch.long))
            ctx.append(int(logits[0, -1].argmax().item()))
            oracle = ctx[:]
    checks["greedy_matches_sequential_argmax_oracle"] = generated == oracle
    tokens = [([2000, 2001, 2002], [2001, 2002, 2003]), ([1710, 1711], [1711, 1712])]
    before = [p.detach().clone() for p in model.parameters()]
    report = evaluate_synthetic_heldout(model, tokens)
    explicit_sum = 0.
    total = 0
    with torch.inference_mode():
        for x,y in tokens:
            logits, _ = model(torch.tensor([x], dtype=torch.long))
            explicit_sum += float(F.cross_entropy(logits[0], torch.tensor(y), reduction="sum").item())
            total += len(x)
    checks["heldout_nll_independent_recompute_and_weights_unchanged"] = (
        report["token_count"] == total
        and math.isclose(report["mean_nll"], explicit_sum/total, rel_tol=0, abs_tol=1e-7)
        and all(torch.equal(a,b) for a,b in zip(before, model.parameters()))
        and report["evaluation_only"] is True)
    status = "PASS" if all(checks.values()) else "FAIL"
    print(json.dumps({"schema":"ttm.p04.independent.synthetic_cpu.qa.v1", "status":status,
                      "checks":checks,"torch":torch.__version__,"no_external_corpus":True,
                      "P01_TEST":"NOT_READ","P04_REAL_HELDOUT":"NOT_OPENED"},sort_keys=True))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
