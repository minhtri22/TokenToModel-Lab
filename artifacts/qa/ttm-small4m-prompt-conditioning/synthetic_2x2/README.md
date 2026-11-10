# TTM-Small4M 2×2 — Synthetic QA evidence index (2026-11-10)

**GitHub is the source of truth.** All files here are synthetic-only (no original corpus, checkpoint, TEST/Q1Q2, owner key). Runner, tests and independent auditor live at [`tools/pilot_t4/prompt_conditioning_2x2/`](../../../../tools/pilot_t4/prompt_conditioning_2x2/).

| Evidence | Exact SHA-256 of original source bytes |
|---|---|
| `SYNTHETIC_RUN_SUMMARY_20261110.json` | `8fc4206137bc5e2e59a48f6d3e2326248afc7c45f319ee8753c81d96927dbad9` |
| `SYNTHETIC_PREFLIGHT_QA_RECEIPT_20261110.json` | `1fe5f96bd950fcdfa6c1084a3327d3d8550bbecbd26870843be23d878333d559` |
| `INDEPENDENT_AUDIT_20261110.json` | `08b9fa2e96aee24723eea972f2f870f620c6ce81153ed157140e9139595f78f0` |
| `UNITTEST_72_OF_72_20261110.txt` | `a8de0ea164b66c2240a75fbee3bf2154cfe577d682561d839acf950370578b74` |
| Full uncompressed `SYNTHETIC_RUN_RESULT.json` | `1f92b9fe5965591ce6f8292e778642081c2ad9c1557ea08b5538f536524ac409` |

The complete **111,962-byte original JSON** is preserved as two GitHub text files containing a deterministic gzip-mtime-0 compressed base64 string, split on a multiple-of-four boundary:
- `SYNTHETIC_FULL_EVIDENCE_GZB64_PART1_OF_2.txt`: Git blob `5bafaf9f206f964e9c2c44160544cbb839ac2e9b`.
- `SYNTHETIC_FULL_EVIDENCE_GZB64_PART2_OF_2.txt`: Git blob `7411455a458de0964ef6450d17e4eb75727b4fec`.
- Concatenated base64 with terminal LF SHA-256: `42e8d48f8ad886ec862d6c9618f53130e39cf1b0b909eb37a30960858e777221`.

To reconstruct within the cloned repository and verify the original full evidence bytes (Python standard library; output stays inside this directory):

```python
from pathlib import Path
import base64, gzip, hashlib
p=Path("artifacts/qa/ttm-small4m-prompt-conditioning/synthetic_2x2")
encoded="".join((p/f"SYNTHETIC_FULL_EVIDENCE_GZB64_PART{i}_OF_2.txt").read_text(encoding="ascii").strip() for i in (1,2))
raw=gzip.decompress(base64.b64decode(encoded))
assert len(raw)==111962
assert hashlib.sha256(raw).hexdigest()=="1f92b9fe5965591ce6f8292e778642081c2ad9c1557ea08b5538f536524ac409"
out=p/"SYNTHETIC_RUN_RESULT_RECONSTRUCTED.json"
if out.exists(): raise FileExistsError(out)
out.write_bytes(raw)
print("TTM_2X2_SYNTHETIC_GITHUB_FULL_LOG=PASS_EXACT_SHA")
```

**Scope:** runner test suite `72/72 PASS`, independent read-only arithmetic auditor and 20 mutated negative fixtures `20/20 rejected`, second 128-step replay **byte-identical**. Number of real training steps = **0**. The HMAC schedule feasibility and equal token-slot budgets are proved *only* on the invented synthetic fixture. The real locked 2,691 TRAIN windows have **not** been inspected in this task.

**Owner decision:** `DESIGN_SYNTHETIC_QA_PASS`; `COLAB_SCIENCE_NO_GO_PENDING_COMBINED_RIGHTS_REAL_MATCHING_EVAL_REVIEW`. See [report](../../../../docs/research/TTM_SMALL4M_2X2_SYNTHETIC_PREFLIGHT_AND_OWNER_FREEZE_20261110.md).

**Next:** single integrated source/rights + TRAIN metadata count-matching + new evaluation/reviewer + Colab runner CPU QA owner decision; do not start new GPU training without explicit approval.
