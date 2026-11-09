# G1 Windows — V2 Python quoting STOP, V3 scoped recovery

Date: 2026-11-09. Target: `TTM_SIX_XMODEL_G1_PRIVATE_MANIFEST_SELFTEST_V3_QUOTING_RECOVERY`.

## Owner-reported V2 evidence

The user ran pinned V2 `G1_MANIFEST_RUNNER_V2.ps1 -Mode SelfTest`. Console readback:

```text
G1_GIT_CONFIGURED_ORIGIN=https://github.com/minhtri22/tokentomodel-lab.git
G1_GIT_EFFECTIVE_ORIGIN=https://github.com/minhtri22/tokentomodel-lab.git
G1_REPO_ORIGIN_DUAL_ATTESTATION=PASS
Traceback (most recent call last):
  File "<string>", line 1, in <module>
TypeError: bad operand type for unary +: 'str'
STOP_PYTHON312_VERSION
STOP_G1_V2_SELFTEST_FAILED
```

Interpretation: dual Git origin is verified PASS. Windows PowerShell 5.1 quoted-native-command marshaling stripped the double-quoted Python literal from a `-c` string, causing a Python TypeError in the version diagnostic. This is **not evidence that Python 3.12 is absent/wrong**. The failure occurred before the Python G1 source SelfTest, all tokenizer downloads, reading TinyStories, and creating the private 128/64/64 manifest. Do not re-run T1 or Qwen3-0.6B.

## New V3 source, no unsafe bypass

Pinned branch: `research/ttm-six-cross-model-representation-transfer-20261109`.

New file: `scripts/research/six_ttm/Run-G1-PrivateManifest-PS51-v3.ps1`. Git blob `13e3dd5824a24af9cadec504add4fddbf570436f`. First commit `784e873b0cb058ab6739d393b9cf7ade00b3bbbc`.

- Preserves both configured and effective git origin checks, each required to match the authorized repository.
- Replaces embedded Python string-literal version print with `python.exe -B -c 'import sys; assert sys.version_info[:2] == (3,12)'` and separate `python.exe --version` readback; no nested quotes passed to Python.
- Replaces source AST check with `ast.parse(pathlib.Path(sys.argv[1]).read_bytes())`, file path as a separate argv token, not embedded Python string.
- Producer Git blob remains exactly `aee230060f8202907953e0eeab0ae5b1099a584e`. Keeps no-overwrite source acquisition, rights opt-in for Seal, pinned QA, project-only I/O. Original V1/V2 STOP history preserved.
- GitHub readback and focused static QA **PASS 9/9**. No PowerShell runtime or Python selftest executed by assistant. No rights approval or G1 science permit is granted.

## Next action

Owner downloads V3 from exact commit to a **fresh** project-local path, verifies Git blob `13e3dd5824a24af9cadec504add4fddbf570436f`, and runs **SelfTest only**. Expected terminal marker: `G1_LOCAL_STEP=SELFTEST_COMPLETED`, with `G1_REPO_ORIGIN_DUAL_ATTESTATION=PASS`, `G1_LOCAL_PYTHON=3.12.x`, `G1_SOURCE_AST_PARSE=PASS`, and `PASS_SYNTHETIC_SELFTEST_NO_FILES_NO_SCIENCE` receipt.

Any new STOP must be preserved as evidence and diagnosed once; no transition to Tokenizers/Seal/QA before a valid SelfTest PASS. No changes to TTM main, PR #12, `lineage.md` or scientific checkpoints.
