# TTM-SM4M-DIAG-Q001 — CPU diagnostic runner candidate

**Status:** LOCAL CANDIDATE · SOURCE-QA ONLY · NO MODEL EXECUTION · NO IMPLEMENTATION BRANCH · INDEPENDENT REVIEW PENDING.

A separate author-authored checker, `qa_crosscheck.py`, additionally tested
21/21 independent *code-path* conditions (NOT independent reviewer identity).
The one-shot Windows wrapper is provided but MUST NOT be invoked before
review/rights gates.

This package is produced in response to owner decision
`GO_SMALL4M_DIAG_SINGLE_SCOPED_IMPLEMENT_AND_RUN_CONDITIONAL`. The decision does
not override Q2/Q3 distinct review, Q4-scoped implementation closure, checkpoint
rights (AD-00/AD-01C/E6), source and runner SHA custody, or I1 negative QA.

## What has run

`python3 ttm_sm4m_diag_q001.py source-qa`: 18/18 in-memory **mock**
fixture/oracle/negative tests. No PyTorch import, no weights, no real tokenizer,
no sealed TEST/FINAL, and no actual experiment fixtures persisted.

## What MUST happen before run

1. A **distinct** reviewer evaluates Q2/Q3 and the exact candidate source and
   gives a source-scoped PASS/HOLD. This author-generated candidate cannot
   self-validate independence.
2. Exact GitHub source pin and implementation I1 runner are archived; independent
   negative QA verifies token shift, target, controls, determinism, budget,
   absent-key counterexamples and source/hash guards.
3. The owner provides a rights-verified, audited private checkpoint step1024,
   valid 2048-vocabulary non-special ID inventory with locked SHA, and explicit
   single CPU run permit. Token IDs in the source-QA mock are **not** legal
   experimental fixtures. Permit must have an independently checked evidence
   pointer, not just a fabricated JSON boolean.
4. The fixed 80-item fixture SHA is frozen **before** any model inference.
5. The local Windows runtime is pinned to Python 3.12 + torch + psutil, CPU FP32
   and run budget 900s / RSS 12GiB / result 1GiB. New experiments are not
   launched before these are verified.

## Protocol caveats

- Source P02 blob: `9762343e06cf800b50574c2871ae1ed58537fb18`;
  configured T4 model has 3,749,376 params, vocab2048, context256, four layers.
- T4 checkpoint SHA256: `cb985751795c8328ad65acf7ca4c1033ce35182c1bfbdb8c38550de629cb271b`.
- 24 TRAIN, 16 recombined, 16 novel-ID, 16 paired value-swap and 8 absent-key.
- Exactly 256 optimizer steps; last context logit is trained to next one-token
  ID. Full-vocab top-1 and 4-way candidate-restricted top-1 must be reported
  separately; restricted-correct does **not** mean tokenizer/decoder bug.
- The novel-ID group is novel relative to this diagnostic TRAIN only; NOT
  necessarily novel relative to original TinyStories pretraining.
- "Target must not be in input" means **the 10th target position cannot be
  included inside the 9-token prompt**. The answer value token may of course
  appear earlier as a `BIND` value, because this is an information retrieval
  task. Confusing those two would create an invalid target leakage guard.

## Execution safeguard

Calling `python3 ttm_sm4m_diag_q001.py run` without all required arguments
fails closed before opening checkpoint. Even with arguments, the runner requires
a permitted exact source SHA, approved distinct review, owner execution GO,
rights, checkpoint byte pin, fixture SHA pin, and token inventory SHA pin. A
local reviewer must verify the permit and related evidence independently; do
not synthesize a permit to bypass gates.

This is a remediation reviewer-candidate source artifact, **not** an accepted
implementation. The historical author MOCK source QA was **18/18**, not 17/17.
Do not promote any source QA score to model QA.


## F01–F10 remediation — new candidate, not I1 PASS

- F01: `release_auth_v2.py` verifies three separate Ed25519 signatures
  (owner, reviewer, rights custodian) against reviewed **code-pinned public keys**.
  No keys are available or inserted now; `AUTHENTICATED_TRUST_ANCHORS_UNAVAILABLE`
  is the mandatory fail-closed outcome. Local permit JSON cannot grant rights.
- F02: The 2048-ID underlying inventory must match its SHA-256 and a complete
  non-special/special/reserved taxonomy. A locally invented 64-hex digest is
  rejected; private bytes are not opened before external signed authorization.
- F03: Future authenticated I1 `fixture-freeze` stores 80 exact case records
  plus 80 per-case and five per-group hashes in a separate private folder.
  I2 must re-read signed and frozen bytes, never regenerate an alternate set.
- F04: Both PowerShell launchers use `$PSScriptRoot` rather than `_tmp`,
  and demand full lowercase runner SHA-256. Windows PS 5.1 execution
  **NOT_EXECUTED** in author test environment.
- F05: `independent_negative_qa_v2.py` is an author-supplied distinct-path
  MOCK adversarial suite; it reported **31/31** under Linux Python 3.13 (historical author-only receipt); this old v2 suite is superseded for the new candidate by v3 and must not be relabeled as independent Windows QA.
  A genuinely separate Windows Python 3.12 reviewer must rerun it.
- F06: AD-00/AD-01C/E6 external rights, signer trust anchors, live checkpoint
  byte custody, tokenizer inventory, and Windows runtime are **NOT_VERIFIED**.
  I1 release and I2 256-step CPU run remain **HOLD/NOT_EXECUTED**.
- F07: If ever admitted, the runner records parameter SHA-256 and L2 norms
  before/after training, strictly positive weight delta and sampled peak RSS.
- F08: The PowerShell process watchdog polls wall time, RSS, stderr/stdout and
  total generated output, and kills the process tree on breach; native Windows
  watchdog negative QA is still **NOT_EXECUTED**.
- F09: Historical README mismatch fixed: 18/18, not 17/17.
- F10: Restricted four-choice options contain gold at index zero and low-sorted
  distractors, so their correct rate is *exploratory and biased*. No inference
  of a decoder defect may be drawn from restricted vs full-vocabulary scores.
  The frozen protocol is unchanged; an alternative hard-distractor design would
  require a separately accepted Q1 amendment.

The historical `SHA256_MANIFEST.json` and `SOURCE_QA_RECEIPT.json` remain
custodial evidence for **original** reviewed commit `fb0bd357...`, not current
source. Consult `TTM_SM4M_DIAG_Q001_F01_F10_REMEDIATION_SOURCE_MANIFEST_20261116.json`
under artifacts/governance for the new reviewed source pins.

Owner's conditional GO stays recorded but is **not equivalent** to authenticated
rights or I1/I2 admission. No private checkpoints, historic TEST/FINAL, or real
experimental fixtures have been accessed in this source-remediation pass.

## Follow-up I1 remediation after distinct source HOLD at `18fabe425...`

- F01: An authenticated release now pins both `D:\WORK\RESEARCH\TokenToModel-Lab` and
  `DESKTOP-4PSD0G2` in source and signed payload. Every project worktree uses
  one canonical `_evidence/ttm_sm4m_diag_q001_onetime_claims` nonce ledger.
  Changing the --root input cannot choose a new ledger. The old nonce path is
  also checked. This prevents ordinary cross-worktree replay **on this host**;
  deliberate deletion of local custody or cross-machine use requires external
  durable adjudication and is NOT proven impossible.
- F04: Direct `run`, `fixture-freeze`, and `release-preflight` now reject
  private file/path escapes before any private data opens. On the real Windows
  machine, test junctions and reparse points independently.
- F05: `independent_negative_qa_v3.py` is a **new author-created** mock/source
  harness for root binding, cross-root claims and source watchdog assertions.
  It does NOT constitute independent QA and DOES NOT exercise a Windows watchdog.
  The historical `independent_negative_qa_v2.py` and its 31/31 receipt remain
  unchanged as historical evidence for an older runner.
- F08: `Watch-TTM-SM4M-ProcessTree-PS51.ps1` is a separately SHA-pinned
  native Windows watcher: cumulative sampled descendant process RSS,
  stdout+stderr plus recursive output, and *postexit* threshold checks.
  `Invoke-DIAG-Q001-Watchdog-NativeNegativeQA-PS51.ps1` defines 5 source-only
  adversarial processes: normal, final oversized output, wall timeout,
  child-memory breach and live orphan after parent exit.
  **Do not claim these cases PASS until native PS5.1/Python3.12 execution
  produces a real receipt.** Sampled RSS alone cannot guarantee a strict
  instantaneous OS memory ceiling without a separately proven Job Object.
- F06 remains hard HOLD: `TRUSTED_ED25519_PUBLIC_KEYS={}`,
  rights AD-00/AD-01C/E6 not attested, tokenizer and exact model bytes not
  read/verified. A local GO string must never be used as authorization.

**I1 state remains HOLD**; owner conditional GO is preserved, I2 has NOT run.
Only the frozen Q1 24+56 / 256 steps / seed and original checkpoint are eligible
for future execution after legitimate admission, no automatic retry.
