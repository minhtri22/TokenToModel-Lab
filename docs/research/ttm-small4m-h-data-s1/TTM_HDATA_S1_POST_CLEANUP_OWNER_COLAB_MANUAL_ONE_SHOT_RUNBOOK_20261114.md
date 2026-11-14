# TTM H-DATA-S1 — Owner Colab T4 one-shot after Drive capacity recovery (2026-11-14)

**Operation:** \`TTM_HDATA_S1_POST_CLEANUP_DRIVE_CAPACITY_AND_ONE_SHOT_READINESS_READBACK_NO_TRAIN\`

**Verdict:** \`GO_SCOPED_OWNER_MANUAL_REDISPATCH_SAME_FROZEN_ONE_SHOT_NO_AUTO_TRAIN\`. Owner reported \`DRIVE_FREE_GIB=4.227\`, \`RUN_ROOT_EXISTS=False\`, \`STORAGE_STATUS=PASS_STORAGE_READY\`, \`SCIENCE_DISPATCH=NOT_EXECUTED\`, \`NEW_FINAL=SEALED\`. Source requires >=2GiB before \`root.mkdir\` and the owner remains responsible for intentionally dispatching once. The historical reason for the first \`CalledProcessError\` is not proven because child stderr was not retained. Never infer efficacy H1>H0 at this stage.

## Frozen assets — do not rebase or change

- Immutable research checkout: \`7aec0d551c930936412b93eb49951bd1597d71b9\`
- Science runner SHA-256: \`eae016e92adc862e71d98920844ebd7c36bacbc3c9157c5a5e33d31aa77ded28\`
- Existing owner GO lock SHA-256: \`85e744a3da8d0e417079f726d95f059ad569a5f13e592ee56c1982dbce0aa540\`
- Existing T4 native resume QA receipt SHA-256: \`c93fe27e275cd7a1bcd80f369b2a54667a3da3a5b6a942482f80c0b80c38af8c\`
- Input P02 checkpoint and TRAIN/VAL pack: locked unchanged. H0/H1: 128 updates each, 4096 labels per update, 2,928 forward windows per arm. New FINAL, old FINAL, NEXT24, TEST and OOD remain sealed.
- Original run root: \`/content/drive/MyDrive/TTM/ttm-small-pilot/ttm_small4m_h_data_s1_20261113/science_one_shot_v1\`

## Exactly one manual owner action

1. Ensure FC01 and any other competing Colab T4 science process are stopped/idle. Do not terminate an unconfirmed active experiment.
2. Open the original H-DATA notebook \`tools/pilot_t4/hdata_s1/TTM_HDATA_S1_T4_OWNER_ONE_SHOT_128X4096_20261113.ipynb\` at the frozen checkout, and rerun H-DATA **cells 1, 2, 3** to restore their H-DATA variables in the shared notebook namespace. Do not copy a \`RUNNER\` value from FC01.
3. Confirm \`H_DATA_S1_PRIVATE_PINS_AND_AES_CIPHERTEXT=PASS\`, \`RUN_ROOT.exists()==False\`, \`shutil.disk_usage(RUN_ROOT.parent).free >= 2*1024**3\`, exact pinned H-DATA source/GO lock and T4 \`torch==2.14.1+cu130\`.
4. In **Cell 4 only**, set \`ARM_ONE_SHOT=True\` and \`RESUME_EXISTING=False\`. Replace only the line \`subprocess.run(cmd,cwd=str(REPO),check=True)\` with the **transport-only output capture** below; this does not change the immutable child runner, its optimizer, sampler, run ID, source hash or scientific contract:

\`\`\`python
from collections import deque
_child_tail = deque(maxlen=80)
with subprocess.Popen(
    cmd, cwd=str(REPO), stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT, text=True, bufsize=1,
) as _child:
    for _line in _child.stdout:
        _child_tail.append(_line)
        print(_line, end="", flush=True)
    _exit = _child.wait()
if _exit:
    print("HDATA_S1_CHILD_EXIT_CODE=", _exit)
    print("HDATA_S1_CHILD_LAST_80_LINES_START")
    print("".join(_child_tail))
    print("HDATA_S1_CHILD_LAST_80_LINES_END")
    raise RuntimeError("H_DATA_S1_CHILD_FAILED_KEEP_ROOT_NO_RESUME")
\`\`\`

5. If execution succeeds, run **Cell 5** exactly once to verify H0 and H1 checkpoints SHA and generate \`READY-last\` owner receipt. Share only the receipt status, SHA-256 and nonprivate progress status with independent reviewer. Do not run FINAL inference or blind scoring in this task.

## Failure policy

If child process stops at any step, **do not rerun Cell 4**, **do not set \`RESUME_EXISTING=True\`**, and do not delete, rename or overwrite the science root. Preserve original stdout/stderr and step-begin/done + READY receipts, then independently adjudicate resume safety against the frozen runner. The temporary ciphertext file is automatically cleaned by the existing Cell 4 context manager. Never publish the AES key, sealed FINAL, private TRAIN examples or model tensors on public GitHub.

## Evidence

- Postcleanup capacity owner receipt on research branch: \`artifacts/qa/ttm-small4m-h-data-s1/drive_cleanup/TTM_HDATA_S1_OWNER_POSTCLEAN_4P227GIB_MANUAL_DISPATCH_GO_20261114.json\`.
- Separate completed storage cleanup: \`TTM_DRIVE_CHECKPOINT_CLEANUP_60_FINAL_OWNER_ADJUDICATION_20261113.json\`.
- No assistant-executed GPU, no new training or inference claim, \`MAIN=UNCHANGED\`.
