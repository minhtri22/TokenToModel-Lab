#!/usr/bin/env python3
"""Read-only comparison. Fail closed if critical workload fields differ."""
import argparse
import json
from pathlib import Path
import math
ROOT = Path(__file__).resolve().parents[1]

def compare(a, b):
    fields = ["workload_id", "dataset_id", "dataset_sha256"]
    mismatched = [f for f in fields if a.get(f) != b.get(f)]
    ea = a.get("environment", {})
    eb = b.get("environment", {})
    for f in ["device", "torch", "os"]:
        if ea.get(f) != eb.get(f): mismatched.append("environment." + f)
    comparable = len(mismatched) == 0
    keys = sorted(a.get("metrics", {}).keys() & b.get("metrics", {}).keys())
    rows = []
    for key in keys:
        av, bv = a["metrics"][key], b["metrics"][key]
        if not isinstance(av, (float, int)) or not isinstance(bv, (float, int)): continue
        delta = bv - av
        pct = 100 * delta / abs(av) if av != 0 else None
        rows.append((key,av,bv,delta,pct))
    return comparable,mismatched,rows

def render(a,b):
    compatible, mismatched, rows = compare(a,b)
    lines = [f'# So sánh {a["run_id"]} → {b["run_id"]}', '',
             f'- Khả năng so sánh (workload parity): {"PARTIAL_CHECK_PASS" if compatible else "NOT_ESTABLISHED"}',
             '- Các trường không khớp: '+(', '.join(mismatched) if mismatched else 'không phát hiện trong các trường đã kiểm'),
             '- Cảnh báo: bộ kiểm này chỉ kiểm một tập trường, không tự xác nhận tương đương về model weights, token length, concurrency, precision hay measurement methodology.', '',
             '| Metric | Baseline | Candidate | Delta | Delta % |', '|---|---:|---:|---:|---:|']
    for k,av,bv,delta,pct in rows:
        lines.append(f'| {k} | {av:.6g} | {bv:.6g} | {delta:+.6g} | {pct:+.3f}%'+' |' if pct is not None else f'| {k} | {av:.6g} | {bv:.6g} | {delta:+.6g} | NA |')
    lines.extend(['','**Không tự kết luận hiệu quả hay nguyên nhân.** Phải có QA và đối chứng thiết kế trước.', ''])
    return '\n'.join(lines)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('baseline_run_id');ap.add_argument('candidate_run_id');ap.add_argument('--output')
    args=ap.parse_args()
    def load(rid):
        if not rid or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-' for c in rid): raise ValueError('Invalid run ID')
        return json.loads((ROOT/'experiments'/'runs'/f'{rid}.json').read_text(encoding='utf-8'))
    report=render(load(args.baseline_run_id),load(args.candidate_run_id))
    if args.output:
        p=Path(args.output)
        if p.exists(): raise FileExistsError('Do not overwrite comparison: '+str(p))
        p.parent.mkdir(parents=True,exist_ok=True);p.write_text(report,encoding='utf-8')
    else: print(report)
if __name__=='__main__': main()
