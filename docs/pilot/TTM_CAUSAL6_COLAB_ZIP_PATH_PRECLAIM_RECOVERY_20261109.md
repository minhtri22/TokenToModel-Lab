# TTM CAUSAL6 — pre-CLAIM Colab ZIP_PATH_REFUSED repair, no science execution

**Date:** 2026-11-09. **Scope:** repair only the Colab private ZIP extraction cell; no change in Causal6 contract, H512 membership, checkpoint, SHA, schedule, optimizer, source science runner, GPU or one-shot RUN_ID.

## Incident and diagnosis

Owner mounted Drive, passed the private ZIP checksum check and encountered `AssertionError: ZIP_PATH_REFUSED` inside the Colab extraction loop at `Path(item.filename)`. Windows `Compress-Archive` may write item names with backslashes; on Linux `pathlib.Path` treats backslashes as literal characters, so valid `input\...` and `code\...` names are refused.

The failure occurred **after** `work.mkdir` and **before** `z.extractall`, preflight or science CLAIM. No evidence of model training. The workaround must accept a preexisting **empty** temporary source directory but refuse any nonempty directory; never automatically delete files, overwrite active checkpoint or bypass SHA checks.

## Safe repair

File `CAUSAL6_COLAB_RECOVER_ZIP_PATH_PRECLAIM_20261109.py` is a standalone recovery cell for the original Colab runtime with previously set owner quota and SHA. File `TTM_CAUSAL6_FREE_T4_ONE_SHOT_COLAB_ZIP_PATH_FIXED_20261109.ipynb` is a revised notebook with the same science preflight/execution cells.

- Normalize ZIP member `\` to `/`, then enforce exactly `input` or `code` as first component.
- Reject absolute/drive paths, dot or dot-dot traversal, NUL, symlinks, duplicate target filenames (case-insensitive), foreign roots and oversized archives.
- Verify ZIP SHA256 `2c6cb72f35eba72d6014f15914d6e9792cbf0bf6774d93e3ff5c53e5c6b9ba9a`, CRC, source presence and H512 public seal (512 stories, 651 windows, 119856 targets, zero forwards).
- Check that Drive science run directory does not already exist, before writing to the controlled temp directory; no automatic rerun if one-shot CLAIM has been consumed.
- Owner must provide actual verified Drive free GiB (>=4), and preflight must confirm Free Tesla T4. The revised standalone notebook retains placeholder 0.0, requiring a real value instead of fabricated quota.
- The repair creates **no** scientific claim and runs **no** model training or inference. After success, run the ORIGINAL PRE-CLAIM cell, then only if PASS consider the original execution cell.

## Fixture-only offline QA

Using synthetic ZIPs (no model, H512 text, real ZIP or GPU):
1. Windows backslash members: PASS safe extraction.
2. POSIX slash members: PASS safe extraction.
3. Traversal member `input\..\evil.txt`: REJECTED.
4. Foreign root `other/file.txt`: REJECTED.

`COLAB_ZIP_PATH_RECOVERY_QA=PASS_4_OF_4`. The specific offending filename in the owner's uploaded private ZIP was not independently inspected in this session. The recovery cell logs raw member names during the owner's Colab run; if unexpected top-level entries remain, it must HOLD and report the preview rather than stripping arbitrary prefixes.

**Governance:** Preserve previous source, one-shot identity and H512 seal. No changes to `lineage.md` (last scientific L0018) or `main`. No fresh upload/repin of the 61 MB private ZIP is needed. No future claim of scientific execution until actual runtime receipt verifies it.
