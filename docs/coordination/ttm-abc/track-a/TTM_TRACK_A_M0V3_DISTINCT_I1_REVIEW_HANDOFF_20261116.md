# HANDOFF — Agent A → Independent I1 Adjudicator · Q001 M0 v3

**Operation:** `A_M0_V3_INTEGRATED_REAL_FIXTURE_RUNNER_CUSTODY_NATIVE_AND_DISTINCT_I1_ADJUDICATION_SINGLE_GATE`  
**Repository:** `minhtri22/TokenToModel-Lab` · **Branch:** `research/ttm-track-a-small4m-diagnosis-20261116` · **PR:** [#33 DRAFT](https://github.com/minhtri22/TokenToModel-Lab/pull/33), stacked on [#28 DRAFT](https://github.com/minhtri22/TokenToModel-Lab/pull/28)  
**Handoff date:** 2026-11-16 · **Source QA pin:** `639a662ef52d028d0b3f07234bdc6d0a5ed5be62`. Later documentation/evidence-only commits do not change these code bytes.  
**Handoff STATUS:** `SOURCE_INTEGRATION_PASS · WINDOWS_MOCK_NEGATIVE_QA_PASS · REAL_FIXTURE_FREEZE_NOT_EXECUTED · INDEPENDENT_I1_REVIEW_NOT_EXECUTED · I1=HOLD_PENDING_REVIEW · I2=NOT_EXECUTED`.

## 1. Assignment and independence

You are a **different Agent (not Agent A)** performing one integrated source/byte custody review. Do not treat Agent A's second, alternative-code checker as independent signoff. Read exact changed source, verify manifests, run an independent negative checker of your own and adjudicate one of `I1_PASS_SCOPED_MEASUREMENT` or `HOLD_I1`. Do not merge, start I2, import/checkpoint-load, publish private tokenizer IDs or replay any historical science. The prior conditional owner GO is not an I1 release permit for a materially amended fixture.

Read first:
- [Handoff A at immutable source pin](https://github.com/minhtri22/TokenToModel-Lab/blob/892594577aa45f3b07be577103dd2355de8cf7dd/docs/coordination/ttm-abc/TTM_TRACK_A_SMALL4M_DIAG_AGENT_HANDOFF_20261116.md)
- [Amended preregistration](https://github.com/minhtri22/TokenToModel-Lab/blob/research/ttm-track-a-small4m-diagnosis-20261116/docs/research/ttm-abc/track-a/Q001_MEASUREMENT_AMENDMENT.md)
- [Integrated source/native QA receipt](https://github.com/minhtri22/TokenToModel-Lab/blob/research/ttm-track-a-small4m-diagnosis-20261116/artifacts/ttm-abc/track-a/M0_V3_INTEGRATED_NATIVE_CUSTODY_QA_20261116.json)
- [Previous M0 mock review](https://github.com/minhtri22/TokenToModel-Lab/blob/research/ttm-track-a-small4m-diagnosis-20261116/artifacts/ttm-abc/track-a/M0_20261116_GOLDBLIND_INDEPENDENT_REVIEW.md) (**same-session algorithmic checker; not your review**)

## 2. Source pins and invariants

| Item | Source / hash / expectation |
|---|---|
| PR #28 unchanged source base | `ebdc54575eed1ff60c402eecf60289f408bb38ca` |
| Original Q001 I1 | `HOLD_I1_RESTRICTED_SCORER_LABEL_LEAKAGE` |
| Frozen old **invalid restricted** fixture | SHA256 `5f1234f583ccf719ca9f0e68de4f47d8b653af777271b8115c5f02307f764e5a` (do not overwrite/reuse) |
| Amended guarded runner | `tools/pilot_t4/direct_failure_diag_q001/preexec_candidate_20261116/ttm_sm4m_diag_q001.py`; SHA256 `ccc4f496edbda23517c8efa6110b447eeab807d84a087b0284277670e78cc73d` |
| v3 scorer/fixture | `tools/pilot_t4/direct_failure_diag_q001/track_a_m0_v3/q001_m0_goldblind.py`; SHA256 `98101e871410e7255cd25f611e5eb9d7068ab264ac162e0af89ef1f1863f6587` |
| v3 fixture contract | `ttm.sm4m.q001.track_a.measurement.v3.integrated` |
| Old-public mock fixture (not real) | SHA256 `f696d20af567ba52dbb9187aba87092829b4da7f3974fbe062608659bd99e726` |
| Private original TRAIN-only BPE manifest | `D:\WORK\RESEARCH\TokenToModel-Lab\_tmp\ttm_t1_real_source_v1\T1_BPE2048_REAL_TRAIN_MANIFEST.json` · SHA256 expected `cba18e60cee3d08a353ee6d4a451017289e45af7b4b1179c87171b9b78d7dfdc` |
| Checkpoint historical custody ONLY | `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b` (**do not load**) |

The runner now imports the exact SHA-pinned v3 scorer and delegates fixture generation, validation, group/case hash manifests and teacher-forced full-vocabulary output metrics to the shared v3 contract. Four-choice is secondary; all ties abstain. Independent heldout RECOMBINED and ABSENT exclude TRAIN key–value bindings, NOVEL_IDS exclude TRAIN key/value token IDs, and 16 counterfactuals **must** remain parent-linked, not independent cases. Source/fixture SHA mismatch must fail closed.

## 3. Verified native QA, and its exact limit

- [GitHub Actions run #43895224590](https://github.com/minhtri22/TokenToModel-Lab/actions/runs/43895224590), Windows Server 2022, Python 3.12.10, Windows PowerShell 5.1 compatibility steps: **PASS**.
- v3 author mock checks **10/10**, expanded adversarial unittest **27/27**, amended guarded runner source QA **18/18**, v3 negative/source QA **45/45**, alternate same-session mock checker PASS.
- PS5.1 freeze OnePack **AST/source safety** PASS. This is *not* execution of private-source freeze. No model, checkpoint or real tokenizer accessed in that CI run. No new Job Object stress evidence is claimed: historical 16/16 Win32 QA is untouched and scoped to older runtime.

The first integration CI exposed a stale assertion and reported 44/45; it was fixed in the *QA checker only* (whitespace-safe path check), with the final 45/45 captured in the later green run above. Preserve the earlier failed run; do not hide it.

## 4. Real fixture freeze — not yet performed

Read-only RemoteDesktop directory listing confirms that the pinned T1 BPE source path exists on host `DESKTOP-4PSD0G2`. **No private bytes were read or checked in this Agent A turn.** A managed Windows command requires `task_job_submit`; attempts to register the root returned `remote project kind changed`, so the native real freeze was **NOT_EXECUTED**. Do not synthesize a real fixture SHA or assume the public mock fixture is equivalent.

A one-shot Windows PowerShell 5.1 script was committed:
`tools/pilot_t4/direct_failure_diag_q001/track_a_m0_v3/Invoke-TrackA-M0V3-RealTokenizer-Freeze-PS51.ps1`

Run it on the owner's **existing** Windows machine once a valid managed task exists or directly under the owner environment. It checks git HEAD, root, Python 3.12, exact original BPE bytes and v3 source SHA **before** freezing 80 cases into a *new, private* `_tmp` directory. It writes a sanitized receipt under `_evidence\ttm-track-a-m0-v3` with only file/case/group digests; no private token IDs. It refuses overwrite and never invokes I2. Do not run it twice or change its paths after a partial failure without adjudicating custody.

Suggested PowerShell 5.1 bootstrap **inside project root**, after reviewing the script:

```powershell
$Root = 'D:\WORK\RESEARCH\TokenToModel-Lab'
$Ref = 'refs/heads/research/ttm-track-a-small4m-diagnosis-20261116'
$RemoteLine = & git -C $Root ls-remote origin $Ref
if ($LASTEXITCODE -ne 0 -or -not $RemoteLine) { throw 'HOLD_REMOTE_REF' }
$ExactHead = ($RemoteLine -split '\s+')[0]
& git -C $Root fetch --no-tags origin $Ref
if ($LASTEXITCODE -ne 0) { throw 'HOLD_FETCH' }
$ScriptSpec = $ExactHead + ':tools/pilot_t4/direct_failure_diag_q001/track_a_m0_v3/Invoke-TrackA-M0V3-RealTokenizer-Freeze-PS51.ps1'
$ScriptPath = Join-Path $Root '_tmp\Invoke-TrackA-M0V3-RealTokenizer-Freeze-PS51.ps1'
if (Test-Path -LiteralPath $ScriptPath) { throw 'HOLD_BOOTSTRAP_ALREADY_EXISTS' }
$Lines = @(& git -C $Root show $ScriptSpec)
if ($LASTEXITCODE -ne 0) { throw 'HOLD_SCRIPT_SOURCE' }
[IO.File]::WriteAllText($ScriptPath, ($Lines -join [Environment]::NewLine), [Text.UTF8Encoding]::new($false))
& $ScriptPath -ExpectedCommit $ExactHead -ExpectedRunnerSha256 'ccc4f496edbda23517c8efa6110b447eeab807d84a087b0284277670e78cc73d'
```

**Expected after verified execution:** a unique real fixture SHA-256 (which is *unknown now*), 80 case digests, five group digests, real source hash match, private freeze receipt + sanitized public candidate, no checkpoint access, zero optimizer steps and no nonce claim. Commit **only sanitized** hash receipt to GitHub and link it in your own independent verdict. Preserve raw fixture privately, never upload it to a public branch.

## 5. Independent adjudication checklist — one gate, no micro-permits

As a different reviewer, you must reproduce:
1. Git SHA equality and exact changed-file scope; no unauthorized PR #28/main/lineage or Track B/C changes.
2. Original T1 BPE source SHA/taxonomy verified **on host**; new v3 fixture bytes frozen and read back deterministically; case- and group-level digests match and historical fixture unchanged.
3. Candidate source cannot read `gold` while constructing options; permuting options, mutating labels, swapping queried bindings, blind fixed-ID ranking, constant logits, unseen IDs and full-vocab vs restricted divergence cannot satisfy a false capability claim.
4. No TRAIN binding leak in groups claiming independence, no parent inflation, no 25%-chance assertion without empirical class balance; teacher-forced ninth-context next-token NLL/rank/full-vocab top-1 remain primary.
5. Native affected-file safety QA (Python 3.12, PS5.1, source pins, private path/overwrite/symlink guards, release and I2 HOLD), and fail-closed permission trust. Inspect existing `owner_internal_admission.py`: it still reads the **historical PR #28 I1 verdict**, which is HOLD. Therefore do not claim the new release has been granted or any I2 path is authorized, even if scoped measurement source is valid.
6. Distinct reviewer identity and independently-authored negative QA provenance. Prior Agent A same-session checker does not count.
7. Issue precisely **one** `I1_PASS_SCOPED_MEASUREMENT` or `HOLD_I1` in GitHub evidence; distinguish source-measurement validity from I2 release authorization.

If the real fixture is missing, a byte hash fails, the runner still permits label-derived candidate ordering, the amended endpoint has no full-vocabulary control, or reviewer independence is unproven: **HOLD_I1**. If all scoped I1 requirements are met, an **I1 PASS (measurement only)** remains separate from I2 authorization, and the old owner-internal release pointer must not be bypassed or silently edited.

## 6. Required handback

Supply **reviewer account/session**, exact live branch HEAD and base, changed-file SHA256, original/private BPE SHA proof, real case/group/fixture digest, negative-control table, native QA command/receipt SHA, independent verdict and blocker if HOLD; publish sanitized evidence to GitHub and update draft PR #33 only. Preserve historical frozen source, original question, checkpoints, `lineage.md` and all scientific results. Do not run I2 or merge.

**One next action (for the recipient Agent):** `A_M0_V3_DISTINCT_REAL_BYTE_CUSTODY_AND_MEASUREMENT_I1_SINGLE_ADJUDICATION`.
