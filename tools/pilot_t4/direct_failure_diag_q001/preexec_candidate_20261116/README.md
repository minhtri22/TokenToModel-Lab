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

This is a local reviewer-candidate source artifact, **not** an accepted
implementation. Do not promote its 17/17 mock source-QA score to model QA.
