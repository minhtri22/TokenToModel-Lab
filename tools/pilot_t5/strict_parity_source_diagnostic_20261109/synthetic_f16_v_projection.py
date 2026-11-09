#!/usr/bin/env python3
"""Synthetic one-token attention V -> output projection F16 rounding demonstration.

Not a simulation of TTM weights. No checkpoint, GGUF, TEST, native backend or
original eight T5 fixture IDs are loaded. CPU-only, deterministic.
"""
from __future__ import annotations
import json
import torch

def main():
    torch.set_num_threads(1)
    samples=[]
    for i in range(8):
        torch.manual_seed(20261109+i)
        value = torch.randn(256, dtype=torch.float32)*0.3
        proj = torch.randn(256,256,dtype=torch.float32)*0.04
        full = proj @ value
        half = proj @ value.to(torch.float16).float()
        samples.append({
            "synthetic_id":i,
            "v_cast_max_abs":float((value-value.to(torch.float16).float()).abs().max()),
            "output_projection_max_abs":float((full-half).abs().max()),
        })
    print(json.dumps({
        "schema":"ttm.t5.f16_v_projection.synthetic_only.v1",
        "scope":"SYNTHETIC_DEMONSTRATION_NOT_TRAINED_PARITY",
        "torch_version":torch.__version__,"sample_count":len(samples),
        "rows":samples,
        "max_projected_error":max(r["output_projection_max_abs"] for r in samples),
        "no_training":True,"no_test":True,"no_native_llama":True,
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
